"""ARM configuration for bass."""

import os.path
import armgliss as arm
import bass

DATADIR = os.path.abspath("data")
CC = "arm-linux-gnueabihf-gcc"
CFLAGS = "-g"
LDFLAGS = "-static -nostartfiles"
INITIAL_SOURCE ="""
	.global	_start

_start:


_exit:
	b	_exit
"""
EXEC_EXT = "elf"

CC_COMMAND = f"{CC} {CFLAGS} -o '%%s' '%%s' {LDFLAGS}"


class Register(bass.Register):

	def __init__(self, name, bank, index):
		bass.Register.__init__(self, name)
		self.bank = bank
		self.index = index


class Arch(bass.Arch):
	"""Architecture representation for ARM."""

	def __init__(self):
		self.regs = None

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
					regs = [Register(name, i, 0)]
				else:
					regs = []
					for j in range(rcount):
						regs.append(Register(fmt % j, i, j))
				bank = bass.RegisterBank(name, regs)
				#print(f"DEBUG: [{name}]")
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


class Simulator(bass.Simulator):

	ARCH = None

	def __init__(self, path):
		bass.Simulator.__init__(self, path)
		self.labels = None
		self.breaks = []
		self.pf = None
		self.loader = None
		self.state = None
		self.sim = None
		self.mem = None
		self.banks =  None

		# load the executable
		self.pf = arm.new_platform()
		self.loader = arm.loader_open(path)
		if self.loader is None:
			raise bass.SimException(f"cannot load {path}")
		arm.loader_load(self.loader, self.pf)
		self.start = arm.loader_start(self.loader)

		print("start = ", self.get_label("_start"))
		# prepare the simulator
		self.state = arm.new_state(self.pf)
		self.sim = arm.new_sim(self.state, self.start, self.get_label("_start"))

	def release(self):
		if self.sim is not None:
			arm.delete_sim(self.sim)
		if self.loader is not None:
			arm.loader_close(self.loader)

	def get_label(self, name):
		if self.labels is None:
			self.labels = {}
			for i in range(0, arm.loader_count_syms(self.loader)):
				sym = arm.loader_sym(self.loader, i)
				self.labels[sym[0]] = sym[1]
		try:
			return self.labels[name]
		except KeyError:
			return None

	def set_break(self, addr):
		self.breaks.append(addr)

	def getNbSyms(self):
		return arm.loader_count_syms(self.loader)

	def getRegisterBank(self,i):
		return arm.get_register_bank(i)

	def getRegister(self,i,j):
		return arm.get_register(self.state, i, j)

	def step(self):
		assert self.sim is not None
		arm.step(self.sim)

	def stepInto(self):
		inst= arm.next_inst(self.sim)
		print("instruction :", inst)
		disasm=arm.disasm(inst)
		adrInst=arm.get_inst_addr(inst)
		print("retour dessassemblage")
		arm.free_inst(inst)
		arm.step(self.sim)
		retour=str(hex(adrInst))
		retour+="	==>	"+disasm
		return retour

	def getNbRegisterBank(self):
		return arm.count_register_banks()

	def nextInstruction(self):
		return arm.next_addr(self.sim)

	def setRegister(self,ri,registre,value):
		arm.set_register(self.state,ri, registre, value)

	def getMemory(self):
		if self.mem is None:
			self.mem = arm.get_memory(self.pf,0)
		return self.mem

	def getRegisterBanks(self):
		#R = None
		Ri = None
		for i in range(0, arm.count_register_banks()):
			bank = arm.get_register_bank(i)
			if bank[0] == 'R':
				#R = bank
				Ri = i
		return Ri

	def getStateMemory(self):
		return arm.get_state_memory(self.state)

	def getState(self):
		return self.state

	def get_pc(self):
		assert self.sim is not None
		return arm.next_addr(self.sim)

	def get_register(self, reg):
		assert self.state is not None
		return arm.get_register(self.state, reg.bank, reg.index)

	def set_register(self, reg, value):
		assert self.state is not None
		arm.set_register(self.state, reg.bank, reg.index, value)

	@staticmethod
	def get_arch():
		if Simulator.ARCH is None:
			Simulator.ARCH = Arch()
		return Simulator.ARCH


def load(path):
	return Simulator(path)


