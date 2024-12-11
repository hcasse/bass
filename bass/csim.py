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

import bass
from bass import arch
from csimui.components import Board
from csimui.util import BoardError

class Arch:
	"""Representation of an architecture."""

	def __init__(self, core):
		self.core = core
		self.registers = None

	def get_name(self):
		return self.core.get_name()

	def get_registers(self):
		"""Get the list of register banks."""
		if self.registers is None:
			for reg in self.core.get_registers():
				bank = bass.RegisterBank()
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
		return arch.Register(reg.get_name(), i, reg)


class Simulator(bass.Simulator):
	"""CSim is a generic simulator for micro-controller boards.
	It support several architecture for the core execution and needs to be
	embedded in a simulator wrapper providing display for the core."""

	ARCH = None

	def __init__(self, template):
		"""Build a simulator for the passed template.
		Raises SimException in case of error when building the board."""
		bass.Simulator.__init__(self, template)
		try:
			self.board = Board(self.get_board_path())
		except BoardError as exn:
			raise bass.SimException(str(exn))

	def load(self, path):
		"""Load the executable with the passed path. If there is an error,
		raises a SimException."""
		try:
			self.board.load_bin(path)
		except BoardError as exn:
			raise bass.SimException(str(exn))

	def reset(self):
		"""Reset the simulator."""
		self.board.reset()

	def release(self):
		"""Release the simulator."""
		self.board.release()
		self.board = None

	def set_break(self, addr):
		"""Set a breakpoint to the given address."""
		pass

	def get_pc(self):
		"""Get the address of the PC."""
		return None

	def next_pc(self):
		"""Get the address of the next instruction."""
		return None

	def step(self):
		"""Execute the current instruction and stop."""
		pass

	def get_register(self, reg):
		"""Get the value of a register."""
		return None

	def set_register(self, reg, value):
		"""Set the value of a register."""
		pass

	def get_arch(self):
		"""Get the architecture of the simulator."""
		return None

	def get_frequency(self):
		"""Get the frequency of the simulator in Hz."""
		return 100

	def get_date(self):
		"""Get the date in cycles."""
		return 0

	def get_byte(self, addr):
		"""Get the byte at the given address."""
		return None

	def get_half(self, addr):
		"""Get unsigned 16b integer."""
		return None

	def get_word(self, addr):
		"""Get unsigned 32b integer."""
		return None

