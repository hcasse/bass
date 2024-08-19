"""ARM configuration for bass."""

import armgliss as arm
import bass

class Register(bass.Register):

	def __init__(self, name, bank, index, format=bass.RegDisplay.SIGNED):
		bass.Register.__init__(self, name)
		self.bank = bank
		self.index = index
		self.fmt = format

	def format(self, value):
		return self.fmt.format(value)

	def get_format(self):
		return self.fmt


class AddrRegister(Register):
	"""Register containing an address."""

	def __init__(self, name, bank, index):
		Register.__init__(self, name, bank, index, bass.RegDisplay.HEX)

	def format(self, value):
		return f"{value:08x}"


class CPSRegister(Register):
	"""Register containing CPSR."""

	MODES = {
		0b0000: "User",
		0b0001: "FIQ",
		0b0010:	"IRQ",
		0b0011: "Super",
		0b0110: "Monit",
		0b0111: "Abort",
		0b1010: "Hyper",
		0b1011: "Undef",
		0b1111: "Sys"
	}

	@staticmethod
	def do_format(value):
		N = "N" if (value >> 31) & 1 else "-"
		Z = "Z" if (value >> 30) & 1 else "-"
		C = "C" if (value >> 29) & 1 else "-"
		V = "V" if (value >> 28) & 1 else "-"
		E = "E" if (value >> 9) & 1 else "-"
		A = "A" if (value >> 8) & 1 else "-"
		I = "I" if (value >> 7) & 1 else "-"
		F = "F" if (value >> 6) & 1 else "-"
		try:
			M = CPSRegister.MODES[value & 0xf]
		except KeyError:
			M = "Invalid"
		return f"{N}{Z}{C}{V} {E}{A}{I}{F} {M}"

	FORMAT = bass.Format(None, do_format, custom = True)

	def __init__(self, name, bank, index):
		Register.__init__(self, name, bank, index, self.FORMAT)


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

	def __init__(self, path):
		bass.Simulator.__init__(self, path)
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
		self.path = path
		self.make()

	def make(self):
		"""Make the simulator. May raise SimException."""

		# loader the executable
		self.pf = arm.new_platform()
		self.mem = arm.get_memory(self.pf, 0)
		self.loader = arm.loader_open(self.path)
		if self.loader is None:
			raise bass.SimException(f"cannot load {self.path}")
		arm.loader_load(self.loader, self.pf)
		self.start = arm.loader_start(self.loader)

		# prepare the simulator
		self.state = arm.new_state(self.pf)
		self.sim = arm.new_sim(self.state, self.start, self.get_label("_start"))

	def reset(self):
		self.release()
		self.make()

	def release(self):
		self.pf = None
		if self.sim is not None:
			arm.delete_sim(self.sim)
			self.sim = None
		if self.loader is not None:
			arm.loader_close(self.loader)
			self.loader = None

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
		self.date += 1

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

	def getMemory(self):
		if self.mem is None:
			self.mem = arm.get_memory(self.pf,0)
		return self.mem

	def getStateMemory(self):
		return arm.get_state_memory(self.state)

	def getState(self):
		return self.state

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


