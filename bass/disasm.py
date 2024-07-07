"""Disassembly module."""

import orchid as orc
from orchid.util import Buffer

class DisasmPane(orc.Component):
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
		self.disasm = None
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
			self.map = {}
			out.write(f'<tbody id="{self.get_id()}-body">')
			out.write("<tr><th>Address</th><th>Code</th><th>Instruction</th></tr>")
			for i, (addr, bytes, inst) in enumerate(self.disasm.get_code()):
				out.write(f"<tr><td>{addr:08x}</td><td>{bytes}</td><td>{inst}</td></tr>")
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
