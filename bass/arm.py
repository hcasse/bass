"""ARM configuration for bass."""

import armgliss as arm
import bass
from bass.arch import *

class Arch(bass.Arch):
	"""Architecture representation for ARM."""

	NAMES = {
		13: "SP",
		14: "LR",
		15: "PC"
	}

	def __init__(self):
		self.regs = None
		self.map = None

	def get_name(self):
		return "ARM"

	def get_registers(self):
		if self.regs is None:
			self.regs = []
			R = None
			CPSR = None
			count = arm.count_register_banks()
			for i in range(count):
				(name, fmt, rcount, _, _) = arm.get_register_bank(i)
				if rcount == 1:
					if name == "CPSR":
						regs = [CPSRegister(name, i, 0)]
					else:
						regs = [Register(name, i, 0)]
				else:
					regs = []
					for j in range(rcount):
						if name == "R" and j >= 13:
							reg = AddrRegister(self.NAMES[j], i, j)
						else:
							reg = Register(fmt % j, i, j)
						regs.append(reg)
				bank = bass.RegisterBank(name, regs)
				if name == "R":
					R = bank
				elif name == "CPSR":
					CPSR = bank
				else:
					self.regs.append(bank)
			assert R is not None
			assert CPSR is not None
			self.regs = [R, CPSR] + self.regs
		return self.regs

	def find_register(self, name):
		"""Find a register by its name. Return None if the register cannot be
		found."""
		if self.map is None:
			self.map = {}
			for bank in self.get_registers():
				for reg in bank.get_registers():
					self.map[reg.get_name()] = reg
		try:
			return self.map[name.upper()]
		except KeyError:
			return None


class Simulator(bass.Simulator):

	ARCH = None

	def __init__(self, template):
		bass.Simulator.__init__(self, template)

		# initialize all
		self.labels = None
		self.breaks = []
		self.pf = None
		self.mem = None
		self.loader = None
		self.state = None
		self.sim = None
		self.mem = None
		self.banks =  None
		self.date = 0
		self.path = None

		# build the simulator
		self.pf = arm.new_platform()
		self.mem = arm.get_memory(self.pf, 0)
		self.state = arm.new_state(self.pf)
		self.sim = arm.new_sim(self.state, 0, 0)

	def load(self, path):
		self.path = path
		self.loader = arm.loader_open(self.path)
		if self.loader is None:
			raise bass.SimException(f"cannot load {self.path}")
		arm.loader_load(self.loader, self.pf)
		self.start = arm.loader_start(self.loader)
		arm.set_next_address(self.sim, self.start)

	def reset(self):
		arm.reset_platform(self.pf)
		arm.reset_state(self.state)
		if self.path is not None:
			self.load(self.path)

	def release(self):
		self.pf = None
		if self.sim is not None:
			arm.delete_sim(self.sim)
			self.sim = None
		if self.loader is not None:
			arm.loader_close(self.loader)
			self.loader = None

	#def get_label(self, name):
	#	if self.labels is None:
	#		self.labels = {}
	#		for i in range(0, arm.loader_count_syms(self.loader)):
	#			sym = arm.loader_sym(self.loader, i)
	#			self.labels[sym[0]] = sym[1]
	#	try:
	#		return self.labels[name]
	#	except KeyError:
	#		return None

	def set_break(self, addr):
		self.breaks.append(addr)

	#def getNbSyms(self):
	#	return arm.loader_count_syms(self.loader)

	#def getRegisterBank(self,i):
	#	return arm.get_register_bank(i)

	#def getRegister(self,i,j):
	#	return arm.get_register(self.state, i, j)

	def step(self):
		assert self.sim is not None
		arm.step(self.sim)
		self.date += 1

	#def stepInto(self):
	#	inst= arm.next_inst(self.sim)
	#	print("instruction :", inst)
	#	disasm=arm.disasm(inst)
	#	adrInst=arm.get_inst_addr(inst)
	#	print("retour dessassemblage")
	#	arm.free_inst(inst)
	#	arm.step(self.sim)
	#	retour=str(hex(adrInst))
	#	retour+="	==>	"+disasm
	#	return retour

	#def getNbRegisterBank(self):
	#	return arm.count_register_banks()

	#def nextInstruction(self):
	#	return arm.next_addr(self.sim)

	#def getMemory(self):
	#	if self.mem is None:
	#		self.mem = arm.get_memory(self.pf,0)
	#	return self.mem

	#def getStateMemory(self):
	#	return arm.get_state_memory(self.state)

	#def getState(self):
	#	return self.state

	def get_pc(self):
		return arm.next_addr(self.sim)

	def next_pc(self):
		pc = arm.next_addr(self.sim)
		decoder = arm.get_sim_decoder(self.sim)
		inst = arm.decode(decoder, pc)
		size = arm.get_inst_size(inst)
		arm.free_inst(inst)
		return pc + size//8

	def get_register(self, reg):
		assert self.state is not None
		return arm.get_register(self.state, reg.bank, reg.index)

	def set_register(self, reg, value):
		assert self.state is not None
		arm.set_register(self.state, reg.bank, reg.index, value)

	def get_date(self):
		return self.date

	def get_byte(self, addr):
		return arm.mem_read8(self.mem, addr)

	def get_half(self, addr):
		return arm.mem_read16(self.mem, addr)

	def get_word(self, addr):
		return arm.mem_read32(self.mem, addr)

	@staticmethod
	def get_arch():
		if Simulator.ARCH is None:
			Simulator.ARCH = Arch()
		return Simulator.ARCH


def load(path):
	return Simulator(path)
