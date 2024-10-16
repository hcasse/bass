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

from bass import Simulator, SimException

class CSim(Simulator):
	"""CSim is a generic simulator for micro-controller boards.
	It support several architecture for the core execution and needs to be
	embedded in a simulator wrapper providing display for the core."""

	def __init__(self, path):
		"""Build a simulator the board in the path.
		Raise SimException if there is an error."""

	def load(self, path):
		"""Load the executable with the passed path."""
		pass

	def reset(self):
		"""Reset the simulator."""
		pass

	def release(self):
		"""Release the simulator."""
		pass

	def get_label(self, name):
		"""Get the name of a label. Return None if the label is not found."""
		return None

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
