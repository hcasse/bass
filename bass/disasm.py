"""Disassembly module."""

import orchid as orc
from orchid.util import Buffer
import bass

class DisasmPane(orc.Component, bass.ApplicationPane):
	"""Display disassembly code."""

	MODEL = orc.Model(
		"disasm-pane",
		style = """
table.disasm {
	overflow: auto;
	border: 0;
	border-collapse: collapse;
}

table.disasm tr td {
	padding: 2px;
	padding-right: 8px;
	font-family: monospace;
}

table.disasm tr td:nth-child(1) {
	min-width: 1.2em;
}


table.disasm tr th {
	text-align: left;
	padding-right: 8px;
	font-weight: normal;
	text-decoration-line: underline;
}

.disasm-current {
	background: yellow;
}

.disasm-selected {
	background: lightblue;
}
"""
)

	def __init__(self):
		orc.Component.__init__(self, self.MODEL)

		self.session = None
		self.disasm = None
		self.sim = None
		self.update_disasm = False
		self.map = None
		self.pc_row = None

		self.add_class('text-back')
		self.add_class('disasm')

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
					bp = ''
				else:
					bp = ' class="disasm-bp"'
				out.write(f"<tr>\
					<td{bp}></td>\
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

	def on_compile_done(self, session):
		print("DEBUG: disasm on_compile_don()")
		self.disasm = None
		self.update_disasm = True
		if self.is_shown():
			self.on_show()

	def on_show(self):
		print("DEBUG: disasm on_show()")
		if self.update_disasm:
			self.update_disasm = False
			try:
				self.set_disasm(self.session.get_project().get_disasm())
			except bass.DisassemblyException:
				self.disasm = None
		if self.sim and self.disasm:
			self.set_pc(self.sim.get_pc())

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



