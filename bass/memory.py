"""Memory display pane."""

import orchid as orc
from orchid.util import Buffer
import bass

class AddressType(orc.Type):

	def __init__(self):
		orc.Type.__init__(self)

	def get_null(self):
		return None

	def as_text(self, value):
		if value is None:
			return ""
		else:
			return str(value)

	def parse(self, text):
		try:
			return int(text, 16)
		except ValueError:
			return None

ADDRESS_TYPE = AddressType()


class MemoryDisplayer(orc.Component):
	"""Component displaying the memory itself."""

	MODEL = orc.Model(
		"bass-binary",
		style = """
.bass-memory {
	overflow-x: auto;
	overflow-y: auto;
}

.bass-memory table {
}
""",
		script = """
function bass_memory_update(msg) {
	let tbody = document.getElementById(msg.id);
	i = 0;
	while(i < msg.sets.length) {
		let p = msg.sets[i];
		let tr = tbody.children[(p >> 4)+1];
		let td = tr.children[(p & 0xf)+1];
		td.classList.add("error-text");
		td.innerText = msg.vals[i].toString(16).padStart(2, '0');
		i++;
	}
	i = 0;
	while(i < msg.resets.length) {
		let p = msg.resets[i];
		let tr = tbody.children[(p >> 4) + 1];
		let td = tr.children[(p & 0xf)+1];
		td.classList.remove("error-text");
		i++;
	}
	console.log("DEBUG:" + JSON.stringify(msg));
}
"""
	)

	def __init__(self):
		orc.Component.__init__(self, model=MemoryDisplayer.MODEL)
		self.base = None
		self.size = None
		self.mem = None
		self.sim = None
		self.add_class("text-back")
		self.add_class("bass-memory")
		self.changes = set()

	def show_mem(self, base, size):
		"""Show the given memory."""

		# read the memory
		self.base = base & 0xfffffff0
		self.size = ((base + size + 15) & 0xfffffff0) - self.base
		self.mem = [0] * self.size

		# generate the content
		self.gen_mem()

	def gen(self, out):
		out.write('<div ')
		self.gen_attrs(out)
		out.write('>')
		if self.mem is None:
			out.write('Nothing to display.')
		else:
			self.gen_content(out)
		out.write('</div>')

	def gen_content(self, out):
		"""Generate the content."""
		out.write(f'<table><tbody id="{self.get_id()}-body">')
		out.write('<tr><td>address</td>')
		for i in range(16):
			out.write(f'<td>{i:1x}</td>')
		out.write('</tr>')
		i = 0
		while i < self.size:
			out.write(f'<tr><td>{self.base + i:08x}</td>')
			for j in range(16):
				out.write(f'<td>{self.mem[i + j]:02x}</td>')
			out.write('</tr>')
			i += 16
		out.write('</tbody></table>')

	def gen_mem(self):
		"""Update the memory from the simulator.."""
		if self.mem is not None:
			for i in range(self.size):
				self.mem[i] = self.sim.get_byte(self.base + i)
			buf = Buffer()
			self.gen_content(buf)
			self.set_content(str(buf))

	def update_mem(self):
		"""Udpate the memory."""
		if self.mem is not None:
			new_changes = set()
			sets = []
			vals = []
			for i in range(self.size):
				byte = self.sim.get_byte(self.base + i)
				if byte != self.mem[i]:
					self.mem[i] = byte
					sets.append(i)
					vals.append(byte)
					new_changes.add(i)
			old_changes = self.changes - new_changes
			resets = list(old_changes)
			self.changes = new_changes
			if sets or resets:
				self.call("bass_memory_update", {
					"id": f"{self.get_id()}-body",
					"sets": sets,
					"vals": vals,
					"resets": resets
				})

	def start_sim(self, sim):
		"""Start a new simulation."""
		self.sim = sim
		self.gen_mem()

	def stop_sim(self):
		"""Stop the simulation."""
		self.sim = None

	def expands_horizontal(self):
		return True

	def expands_vertical(self):
		return True


class MemoryPane(orc.VGroup, bass.ApplicationPane):
	"""Application pane to show memory."""

	MODEL = orc.Model(
		"bass-memory"
	)

	def __init__(self):
		self.addr = orc.Var(None, ADDRESS_TYPE,
			help="Address of displayed memory.")
		self.size = orc.Var(64,
			help="Size of shown memory (in bytes).")
		add_action = orc.Action(self.add_chunk,
			enable=(self.addr != None) & (self.size > 0),
			icon=orc.Icon(orc.IconType.CHECK),
			help="Display the configured chunk of memory")
		self.selector = orc.HGroup([
			orc.Field(self.addr, place_holder="address", weight=2),
			orc.Field(self.size, place_holder="size", weight=1),
			orc.Button(add_action)
		])
		self.selector.disable()
		self.mdisplay = MemoryDisplayer()
		orc.VGroup.__init__(self, [
			self.selector,
			self.mdisplay
		], model=MemoryPane.MODEL)

	def expands_horizontal(self):
		return True

	def expands_vertical(self):
		return True

	def add_chunk(self, interface):
		"""Add a chunk display."""
		print("DEBUG:", ~self.addr, ":", ~self.size)
		self.mdisplay.show_mem(~self.addr, ~self.size)

	def on_sim_start(self, session, sim):
		self.selector.enable()
		self.mdisplay.start_sim(sim)

	def on_sim_stop(self, session, sim):
		self.selector.disable()
		self.mdisplay.stop_sim()

	def on_sim_update(self, session, sim):
		self.mdisplay.update_mem()
