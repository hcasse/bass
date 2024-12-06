#
#	BASS is an online training assembly simulator.
#	Copyright (C) 2024 University of Toulouse <hugues.casse@irit.fr>
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""ARM configuration for bass."""

import armgliss as arm
import bass
from bass.arch import *

class Arch(bass.Arch):
	"""Architecture representation for ARM."""

	NAMES = {
		"R13": "SP",
		"R14": "LR",
		"R15": "PC",
	}

	def __init__(self):
		self.regs = None
		self.map = None

	def get_name(self):
		return "ARM"

	def get_registers(self):
		if self.regs is None:
			self.regs = []
			R = []
			CPSR = []
			count = arm.count_register_banks()
			for bank in range(count):
				(name, fmt, rcount, _, _) = arm.get_register_bank(bank)
				if rcount == 1:
					if name == "CPSR":
						CPSR.append(CPSRegister(name, 0, handle=bank))
					else:
						self.regs.append(Register(name, 0, handle=bank))
				else:
					for i in range(rcount):
						iname = fmt % i
						try:
							reg = AddrRegister(self.NAMES[iname], i, handle=bank)
						except KeyError:
							reg = Register(iname, i, handle=bank)
						if name == "R":
							R.append(reg)
						else:
							self.regs.append(reg)
			assert len(R) != 0
			assert len(CPSR) != 0
			self.regs = R + CPSR + self.regs
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
		self.start = None

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

	def set_break(self, addr):
		self.breaks.append(addr)

	def step(self):
		assert self.sim is not None
		arm.step(self.sim)
		self.date += 1

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
		return arm.get_register(self.state, reg.handle, reg.index)

	def set_register(self, reg, value):
		assert self.state is not None
		arm.set_register(self.state, reg.handle, reg.index, value)

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
