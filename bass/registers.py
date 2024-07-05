"""Pane displaying the registers."""

import orchid as orc

class RegisterPane(orc.VGroup):

	def __init__(self):

		# build field
		self.fields = [orc.Field(size=10) for _ in range(13)]
		for i in range(4):
			self.fields.append(orc.Field(size=10,read_only=True))
		#self.fieldR0= orc.Field(size=10)

		orc.VGroup.__init__(self, [
			#orc.Button("Reset", on_click=self.reset),
			orc.Label("Registers"),
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

	def updateFieldRegister(self):
		"""
			Update the register of the interface.
		"""
		self.R = None
		self.Ri = None
		registerBanks=self.sim.getNbRegisterBank()
		print("NB banque de registre = ",registerBanks)
		for i in range(0, registerBanks):
			bank = self.sim.getRegisterBank(i)
			if bank[0] == 'R':
				self.R = bank
				self.Ri = i
			if bank[2] == 1:
				self.fieldRegistre[16].set_value(hex(self.sim.getRegister(i, 0)))
			for j in range(0, bank[2]):
				self.fieldRegistre[j].set_value(hex(self.sim.getRegister(i, j)))

	def updateRegisterFromField(self):
		"""
			Update register value from field.
		"""
		Ritemp= self.sim.getRegisterBanks()
		for i in range(13):
			self.sim.setRegister(Ritemp,i,self.fieldRegistre[0].get_content())

