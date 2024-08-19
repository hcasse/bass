"""Memory display pane."""

import orchid as orc
from orchid import not_null
from orchid.util import Buffer
import bass


class AddressType(orc.Type):
	"""Type to represent addresses."""

	def __init__(self):
		orc.Type.__init__(self)
		self.sim = None
		self.disasm = None

	def set_sim(self, sim):
		"""Set the current simulator."""
		self.sim = sim

	def set_disasm(self, disasm):
		self.disasm = disasm

	def get_null(self):
		return None

	def as_text(self, value):
		if value is None:
			return ""
		else:
			return value

	def parse(self, text):
		addr = self.address(text)
		if addr is None:
			return None
		else:
			return text

	def get_base(self, text):
		"""Get the value as an address."""
		text = text.strip()

		# an address?
		try:
			return int(text, 16)
		except ValueError:
			pass

		# a label?
		addr = self.disasm.find_label(text)
		if addr is not None:
			return addr

		# a register?
		reg = self.sim.get_arch().find_register(text)
		if reg is not None:
			return self.sim.get_register(reg)

		# unknown
		return None


	def address(self, text):
		"""Get the value as an address."""

		def const(text):
			try:
				return int(text, 16)
			except ValueError:
				return None

		def combine(p, f):
			base = self.get_base(text[:p])
			offset = const(text[p+1:])
			if base is None or offset is None:
				return None
			else:
				return f(base, offset)

		p = text.find('+')
		if p >= 0:
			return combine(p, lambda x,y: x + y)

		p = text.find('-')
		if p >= 0:
			return combine(p, lambda x,y: x - y)

		return self.get_base(text)


ADDRESS_TYPE = AddressType()


class DisplayType:
	"""Type of display for data in memory."""

	def __init__(self, label, size, load=None, display=None, clazz=None):
		self.label = label
		self.size = size
		self.load = load
		self.display = display
		self.clazz = clazz

	def __str__(self):
		return self.label


class Displays:
	"""Displays for the memory."""

	SPEC_CHARS = {
		 8: "\u21a4",
		 9: "\u21b9",
		10: "\u23ce",
		32: "\u2423"
	}

	@staticmethod
	def load_byte(sim, addr):
		return sim.get_byte(addr)

	@staticmethod
	def load_s16(sim, addr):
		data =sim.get_half(addr)
		if data < 0x8000:
			return data
		else:
			return -(0x10000 - data)

	@staticmethod
	def load_u16(sim, addr):
		return sim.get_half(addr)

	@staticmethod
	def load_s32(sim, addr):
		data =sim.get_word(addr)
		if data < 0x80000000:
			return data
		else:
			return -(0x100000000 - data)

	@staticmethod
	def load_u32(sim, addr):
		return sim.get_word(addr)

	@staticmethod
	def display_byte(x):
		return f"{x:02x}"

	@staticmethod
	def display_hex16(x):
		return f"{x:04x}"

	@staticmethod
	def display_hex32(x):
		return f"{x:08x}"

	@staticmethod
	def display_char(x):
		if x <= 32 or x >= 128:
			if x in Displays.SPEC_CHARS:
				return Displays.SPEC_CHARS[x]
			else:
				return f"{x:02x}"
		else:
			return chr(x)

	LIST = [
		DisplayType("Byte", 1, load=load_byte, display=display_byte),
		DisplayType("Signed 16b", 2, load=load_s16, display=str, clazz="bass-16"),
		DisplayType("Unsign. 16b", 2, load=load_u16, display=str, clazz="bass-16"),
		DisplayType("Hexa. 16b", 2, load=load_u16, display=display_hex16),
		DisplayType("Signed 32b", 4, load=load_s32, display=str, clazz="bass-32"),
		DisplayType("Unsign. 32b", 4, load=load_u32, display=str, clazz="bass-32"),
		DisplayType("Hexa. 32b", 4, load=load_u32, display=display_hex32),
		DisplayType("Character", 1, load=load_byte, display=display_char)
	]


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

.bass-memory table th {
	font-weight: normal;
	text-align: right;
	border-bottom: 1px solid black;
}

.bass-memory table td {
	text-align: right;
}

.bass-16 th:not(:first-child) {
	min-width: 4em;
}

.bass-32 th:not(:first-child) {
	min-width: 8em;
}

.bass-target {
	background-color: lightblue;
}
""",
		script = """
function bass_memory_update(msg) {
	let tbody = document.getElementById(msg.id);
	let len = msg.len;
	let i = 0;
	while(i < msg.sets.length) {
		let p = msg.sets[i];
		let tr = tbody.children[(p/len | 0)+1];
		let td = tr.children[(p & (len-1))+1];
		td.classList.add("error-text");
		td.innerText = msg.vals[i];
		i++;
	}
	i = 0;
	while(i < msg.resets.length) {
		let p = msg.resets[i];
		let tr = tbody.children[(p/len | 0) + 1];
		let td = tr.children[(p & (len-1))+1];
		td.classList.remove("error-text");
		i++;
	}
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
		self.type = None
		self.target = None

	def show_mem(self, base, size, type):
		"""Show the given memory."""

		# cleanup old type if any
		if self.mem is not None and self.type.clazz is not None:
			self.remove_class(self.type.clazz)

		# read the memory
		self.base = base & 0xfffffff0
		self.size = (((base + size*type.size + 15) & 0xfffffff0) - self.base) // type.size
		self.mem = [0] * self.size
		self.type = type
		if type.clazz is not None:
			self.add_class(type.clazz)
		self.target = (base - self.base) // type.size

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
		out.write('<tr><th>address</th>')
		for i in range(0, 16, self.type.size):
			out.write(f'<th>{i:1x}</th>')
		out.write('</tr>')
		i = 0
		while i < self.size:
			out.write(f'<tr><td>{self.base + i:08x}</td>')
			for j in range(16//self.type.size):
				if i + j == self.target:
					cls = ' class="bass-target"'
				else:
					cls = ''
				out.write(f'<td{cls}>{self.type.display(self.mem[i + j])}</td>')
			out.write('</tr>')
			i += 16 // self.type.size
		out.write('</tbody></table>')

	def gen_mem(self):
		"""Update the memory from the simulator.."""
		if self.mem is not None:
			for i in range(self.size):
				self.mem[i] = self.type.load(self.sim, self.base + i*self.type.size)
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
				data = self.type.load(self.sim, self.base + i*self.type.size)
				if data != self.mem[i]:
					self.mem[i] = data
					sets.append(i)
					vals.append(self.type.display(data))
					new_changes.add(i)
			old_changes = self.changes - new_changes
			resets = list(old_changes)
			self.changes = new_changes
			if sets or resets:
				self.call("bass_memory_update", {
					"id": f"{self.get_id()}-body",
					"len": 16//self.type.size,
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
		self.type = orc.Var(0, orc.Types.enum(Displays.LIST, 0),
			help="Type of display.")
		self.size = orc.Var(64,
			help="Size of shown memory (in bytes).")
		add_action = orc.Action(self.add_chunk,
			enable=not_null(self.addr) & (self.size > 0),
			icon=orc.Icon(orc.IconType.CHECK),
			help="Display the configured chunk of memory")
		self.selector = orc.HGroup([
				orc.Field(self.addr, place_holder="address", weight=2),
				orc.Field(self.size, place_holder="size", weight=1),
				orc.Select(self.type),
				orc.Button(add_action)
			]).key(orc.Key.ENTER, add_action)
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
		self.mdisplay.show_mem(
			ADDRESS_TYPE.address(~self.addr),
			~self.size,
			Displays.LIST[~self.type])

	def on_sim_start(self, session, sim):
		self.selector.enable()
		ADDRESS_TYPE.set_sim(sim)
		self.mdisplay.start_sim(sim)

	def on_sim_stop(self, session, sim):
		self.selector.disable()
		self.mdisplay.stop_sim()

	def on_sim_update(self, session, sim):
		self.mdisplay.update_mem()

	def on_compiled(self, session):
		ADDRESS_TYPE.set_disasm(session.get_project().get_disasm())
