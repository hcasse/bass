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

"""Common architecture useful definitions."""

from enum import IntEnum

from bass import Format, MessageException, RegDisplay

class Run(IntEnum):
	OK = 0		# execution reached end
	BP = 1		# breakpoint encountered


class SimException(MessageException):
	"""Exception thrown when an error arises in the simulation."""

	def __init__(self, msg):
		MessageException.__init__(self, msg)


class AbstractRegister:
	"""Represents a register in the simulator. Handle may be any value to
	represent register in the underlying simulator."""

	def __init__(self, name, handle=None):
		self.name = name
		self.handle = handle

	def get_name(self):
		"""Get the register name."""
		return self.name

	def format(self, value):
		"""Get formatted value of the register for human display."""
		return str(value)

	def get_format(self):
		"""Get the format used by this register."""
		pass

	def get_handle(self):
		"""Get the handle of this register."""
		return self.handle


class Register(AbstractRegister):
	"""Simple decimal register displat."""

	def __init__(self, name, index, format=RegDisplay.SIGNED, handle=None):
		AbstractRegister.__init__(self, name, handle)
		self.index = index
		self.fmt = format

	def format(self, value):
		return self.fmt.format(value)

	def get_format(self):
		return self.fmt

	def get_index(self):
		"""Get the index of the register."""
		return self.index


class AddrRegister(Register):
	"""Register containing an address."""

	def __init__(self, name, index, handle=None):
		Register.__init__(self, name, index, RegDisplay.HEX, handle)

	def format(self, value):
		return f"{value:08x}"


class CPSRegister(Register):
	"""Register containing ARM CPSR."""

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

	FORMAT = Format(None, do_format, custom = True)

	def __init__(self, name, index, handle=None):
		Register.__init__(self, "CPSR", index, self.FORMAT, handle)


class Arch:
	"""Representation of an architecture."""

	def get_name(self):
		"""Get the name of the architecture."""
		return "<no name>"

	def get_registers(self):
		"""Get the list of register banks."""
		return []

	def find_register(self, name):
		"""Find a register by its name. Return None if the register cannot be
		found."""
		return None


class Simulator:
	"""Interface to the simulator."""

	def __init__(self, template):
		"""Build a simulator."""
		self.template = template

	def get_template(self):
		"""Get the template that supports the simulator."""
		return self.template

	def load(self, path):
		"""Load the executable with the passed path. If there is an error,
		raises a SimException."""
		pass

	def reset(self):
		"""Reset the simulator."""
		pass

	def release(self):
		"""Release the simulator."""
		pass

	def set_breakpoint(self, addr):
		"""Set a breakpoint to the given address."""
		pass

	def clear_breakpoint(self, addr):
		"""Clear a breakpoint."""
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

	def run(self, time):
		"""Run the simulator the time in cycle.
		Returns a result of type Run."""
		return Run.OK

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

	def get_board(self):
		"""If any,n get the CSIM board of the simulation.
		If there is no board, return None."""
		return None


