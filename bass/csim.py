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

"""CSim class module for interconnection with CSim library."""

from csim import Board, BoardError
from bass import arch


class Arch(arch.Arch):
	"""Representation of an architecture."""

	@staticmethod
	def makeArmR(reg, i):
		if i == 13:
			return arch.AddrRegister("SP", i, handle=reg)
		elif i == 14:
			return arch.AddrRegister("LR", i, handle=reg)
		elif i == 15:
			return arch.AddrRegister("PC", i, handle=reg)
		else:
			return arch.Register(reg.make_name(i), i, handle=reg)

	MAP = {
		("arm", "CPSR"):
			lambda reg, i: arch.CPSRegister("CPSR", i, handle=reg),
		("arm", "R"):
			lambda reg, i: Arch.makeArmR(reg, i)
	}

	def __init__(self, core):
		self.core = core
		self.registers = None
		self.name = self.core.get_name()

	def get_registers(self):
		"""Get the list of register banks."""
		if self.registers is None:
			self.registers = []
			for reg in self.core.get_registers():
				for i in range(reg.get_count()):
					self.registers.append(self.make_register(reg, i))
		return self.registers

	def find_register(self, name):
		for reg in self.get_registers():
			if name == reg.get_name():
				return reg
		return None

	def make_register(self, reg, i):
		"""Build a BASS register from a CSIM Register."""
		try:
			return self.MAP[(self.core.get_component_name(), reg.get_name())](reg, i)
		except KeyError:
			return arch.Register(reg.make_name(i), i, handle=reg)


class Simulator(arch.Simulator):
	"""CSim is a generic simulator for micro-controller boards.
	It support several architecture for the core execution and needs to be
	embedded in a simulator wrapper providing display for the core."""

	def __init__(self, template):
		"""Build a simulator for the passed template.
		Raises SimException in case of error when building the board."""
		arch.Simulator.__init__(self, template)
		try:
			self.board = Board(template.get_board_path())
		except BoardError as exn:
			raise arch.SimException(f"cannot load board {template.get_board_path()}: {exn}")
		self.arch = Arch(self.board.get_core())
		self.breaks = []

	def load(self, path):
		"""Load the executable with the passed path. If there is an error,
		raises a SimException."""
		try:
			self.board.load_bin(path)
		except BoardError as exn:
			raise arch.SimException(f"error during load of {path}: {exn}.")

	def reset(self):
		"""Reset the simulator."""
		self.board.reset()

	def release(self):
		"""Release the simulator."""
		self.board.release()
		self.board = None

	def set_break(self, addr):
		"""Set a breakpoint to the given address."""
		self.breaks.append(addr)

	def get_pc(self):
		"""Get the address of the PC."""
		return self.board.get_pc()

	def next_pc(self):
		"""Get the address of the next instruction."""
		return self.board.get_pc() + self.board.inst_size()

	def step(self):
		"""Execute the current instruction and stop."""
		self.board.run(1)

	def get_register(self, reg):
		"""Get the value of a register."""
		return reg.get_handle().get_value(reg.get_index())

	def set_register(self, reg, value):
		"""Set the value of a register."""
		return reg.get_handle().set_value(reg.get_index(), value)

	def get_arch(self):
		"""Get the architecture of the simulator."""
		return self.arch

	def get_frequency(self):
		"""Get the frequency of the simulator in Hz."""
		return 1000

	def get_date(self):
		"""Get the date in cycles."""
		return self.board.get_date()

	def get_byte(self, addr):
		"""Get the byte at the given address."""
		return self.board.byte_at(addr)

	def get_half(self, addr):
		"""Get unsigned 16b integer."""
		return self.board.half_at(addr)

	def get_word(self, addr):
		"""Get unsigned 32b integer."""
		return self.board.word_at(addr)

