"""Pane displaying the registers."""

import orchid as orc

class RegisterPane(orc.VGroup):

	def __init__(self):

		# build field
		self.fields = [orc.Field(size=10) for _ in range(13)]
		for i in range(4):
			self.fields.append(orc.Field(size=10,read_only=True))
		self.fieldR0= orc.Field(size=10)

		orc.VGroup.__init__(self, [
			orc.Button("Reset", on_click=self.reset),
			orc.HGroup([orc.Label("R0"), self.fields[0]]),
			orc.HGroup([orc.Label("R1"), self.fields[1]]),
			orc.HGroup([orc.Label("R2"), self.fields[2]]),
			orc.HGroup([orc.Label("R3"), self.fields[3]]),
			orc.HGroup([orc.Label("R4"), self.fields[4]]),
			orc.HGroup([orc.Label("R5"), self.fields[5]]),
			orc.HGroup([orc.Label("R6"), self.fields[6]]),
			orc.HGroup([orc.Label("R7"), self.fields[7]]),
			orc.HGroup([orc.Label("R8"), self.fields[8]]),
			orc.HGroup([orc.Label("R9"), self.fields[9]]),
			orc.HGroup([orc.Label("R10"), self.fields[10]]),
			orc.HGroup([orc.Label("R11"), self.fields[11]]),
			orc.HGroup([orc.Label("R12"), self.fields[12]]),
			orc.HGroup([orc.Label("sp"), self.fields[13]]),
			orc.HGroup([orc.Label("lr"), self.fields[14]]),
			orc.HGroup([orc.Label("pc"), self.fields[15]]),
			orc.HGroup([orc.Label("CPSR"), self.fields[16]])
		])

	def reset(self):
		"""Reset the registers."""
		pass

	def init(self):
		"""Initialize the register to 0."""
		for i in range(13):
			self.fields[i].set_value(hex(0))
