"""Disassembly module."""

import orchid as orc
from orchid.util import Buffer
import bass

class DisasmPane(orc.Component, bass.ApplicationPane, orc.SetObserver):
	"""Display disassembly code."""

	MODEL = orc.Model(
		"disasm-pane",
		style = """
table.disasm {
	overflow: auto;
	border: 0;
	border-collapse: collapse;
	cursor: grab;
	user-select: none;
}

table.disasm tr td {
	padding: 2px;
	padding-right: 8px;
	font-family: monospace;
}

table.disasm tr td:nth-child(1) {
	min-width: 8px;
}

table.disasm tr td:nth-child(2) {
	padding-left: 4px: ;
}

table.disasm tr.disasm-bp td:nth-child(1) {
	background-color: red;
	border-radius: 12px;
	padding-right: 0;
}

table.disasm tr th {
	text-align: left;
	padding-right: 8px;
	font-weight: normal;
	text-decoration-line: underline;
}

.disasm-current {
	background: yellow !important;
}

.disasm-selected {
	background: lightblue;
}
""",
	script = """
function disasm_double_click(disasm, event) {
	var item = event.target;
	if(item.tagName == "TD")
		item = item.parentNode;
	if(item.tagName != "TR")
		return;
	let i = ui_index(item);
	console.log("i = " + i);
	if(i > 0)
		ui_send({id: disasm.id, action: "bp", index: i-1 });
}

function disasm_single_click(disasm, event) {
	var item = event.target;
	if(item.tagName == "TD")
		item = item.parentNode;
	if(item.tagName != "TR")
		return;
	let i = ui_index(item);
	console.log("i = " + i);
	if(i > 0)
		ui_send({id: disasm.id, action: "select", index: i-1 });
}
"""
)
	BREAKPOINT = "disasm-bp"
	SELECTED = "disasm-selected"

	def __init__(self):
		orc.Component.__init__(self, self.MODEL)

		self.session = None
		self.disasm = None
		self.sim = None
		self.update_disasm = False
		self.map = None				# address -> index
		self.pc_row = None
		self.breakpoints = None
		self.selected = None

		self.add_class('text-back')
		self.add_class('disasm')
		self.set_attr("ondblclick", "disasm_double_click(this, event);")
		self.set_attr("onclick", "disasm_single_click(this, event);")

	def deselect(self):
		"""Remove the selection."""
		print("DEBUG: deselect!")
		if self.selected is not None:
			self.remove_class(self.SELECTED,
				id=f"{self.get_id()}-body",
				nth=self.selected+1)
			self.selected = None

	def select(self, n):
		"""Select the active line."""
		self.deselect()
		self.selected = n
		if self.selected is not None:
			self.add_class(self.SELECTED,
				id=f"{self.get_id()}-body",
				nth=self.selected+1)

	def gen(self, out):
		out.write("<table ")
		self.gen_attrs(out)
		out.write(">")
		self.gen_content(out)
		out.write("</table>")

	def expands_horizontal(self):
		return True

	def expands_vertical(self):
		return True

	def gen_content(self, out):
		"""Generate the content of the pane."""
		if self.disasm is None:
			out.write("<tr><td>Nothing to display.</td></tr>")
		else:
			bps = self.session.get_breakpoints()
			self.map = {}
			out.write(f'<tbody id="{self.get_id()}-body">')
			out.write("<tr><th></th><th>Address</th><th>Code</th><th>Instruction</th></tr>")
			for i, (addr, bytes, inst) in enumerate(self.disasm.get_code()):
				if addr in bps and bytes:
					bp = f' class="{self.BREAKPOINT}"'
				else:
					bp = ''
				out.write(f"<tr{bp}>\
					<td></td>\
					<td>{addr:08x}</td>\
					<td>{bytes}</td>\
					<td>{inst}</td></tr>")
				if bytes:
					self.map[addr] = i
			out.write('</tbody>')

	def set_disasm(self, disasm):
		"""Change the displayed disassembly."""
		self.disasm = disasm
		if self.online():
			buf = Buffer()
			self.gen_content(buf)
			self.set_content(str(buf))

	def set_pc(self, addr):
		"""Change the address of the PC (and corresponding highlighted line)."""
		try:
			new_pc_row = self.map[addr] + 1
		except KeyError:
			new_pc_row = None
		if new_pc_row != self.pc_row:
			if self.pc_row is not None:
				self.remove_class('disasm-current',
					id=f"{self.get_id()}-body", nth=self.pc_row)
			self.pc_row = new_pc_row
			if self.pc_row is not None:
				self.add_class('disasm-current',
					id=f"{self.get_id()}-body", nth=self.pc_row)

	def on_begin(self, session):
		self.session = session
		session.get_breakpoints().add_observer(self)
		session.get_current_addr().add_observer(self)

	def on_compile_done(self, session):
		self.disasm = None
		self.update_disasm = True
		self.deselect()
		if self.is_shown():
			self.on_show()

	def on_show(self):
		orc.Component.on_show(self)
		if self.update_disasm:
			self.update_disasm = False
			try:
				self.set_disasm(self.session.get_project().get_disasm())
			except bass.DisassemblyException:
				self.disasm = None
		if self.sim and self.disasm:
			self.set_pc(self.sim.get_pc())

	def enable_breakpoint(self, addr):
		try:
			i = self.map[addr]
			self.add_class(self.BREAKPOINT, f"{self.get_id()}-body", nth=i+1)
		except KeyError:
			pass

	def disable_breakpoint(self, addr):
		try:
			i = self.map[addr]
			self.remove_class(self.BREAKPOINT, f"{self.get_id()}-body", nth=i+1)
		except KeyError:
			pass

	def on_sim_start(self, session, sim):
		self.sim = sim
		if self.is_shown() and self.disasm:
			self.set_pc(sim.get_pc())

	def on_sim_stop(self, session, sim):
		self.sim = None
		self.set_pc(None)

	def on_sim_update(self, session, sim):
		if self.is_shown() and self.disasm:
			self.set_pc(sim.get_pc())

	def on_add(self, set, item):
		if self.disasm:
			self.enable_breakpoint(item)

	def on_remove(self, set, item):
		if self.disasm:
			self.disable_breakpoint(item)

	def on_clear(self, set):
		for bp in ~set:
			self.on_remove(set, bp)

	def receive(self, msg, handler):
		if msg["action"] == "bp":
			addr = self.disasm.get_code()[msg["index"]][0]
			if addr not in self.session.get_breakpoints():
				self.session.get_breakpoints().add(addr)
			else:
				self.session.get_breakpoints().remove(addr)
		elif msg["action"] == "select":
			addr = self.disasm.get_code()[msg["index"]][0]
			self.session.get_current_addr().set(addr)
		else:
			orc.Component.receive(self, msg, handler)

	def update(self, subject):
		if self.disasm is not None:
			if ~subject is None:
				self.deselect()
			else:
				try:
					i = self.map[~subject]
					self.select(i)
				except KeyError:
					self.deselect()

