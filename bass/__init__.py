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

"""Main module of the BASS."""


from enum import Enum
import importlib

from orchid import matches


def project_name_pred(var):
	"""Build a predicate for a project name."""
	return matches(var, "[a-zA-Z0-9_+=-]+")

def find_symbol(path):
	"""Find a symbol from its name. Return the class or None."""
	comps = path.split('.')
	cls = comps[-1]
	path = '.'.join(comps[:-1])
	try:
		mod = importlib.import_module(path)
		return mod.__dict__[cls]
	except (ModuleNotFoundError, KeyError):
		return None

class MessageException(Exception):
	"""Base class of exception supporting a message."""

	def __init__(self, msg):
		Exception.__init__(self)
		self.msg = msg

	def __str__(self):
		return self.msg


class SimException(MessageException):
	"""Exception thrown when an error arises in the simulation."""

	def __init__(self, msg):
		MessageException.__init__(self, msg)


class Format:
	"""Format to display and parse data."""

	def __init__(self, parse, format, custom = False):
		self.parse = parse
		self.format = format
		self.custom = custom

class RegDisplay:

	@staticmethod
	def unsigned(val):
		if val >= 0:
			return val
		else:
			return val + 0x100000000

	@staticmethod
	def on_exe(f):
		def convert(val):
			try:
				return f(val)
			except ValueError:
				return None
		return convert

	HEX = Format(
		on_exe (lambda v: int(v, 16)),
		lambda v: f"{RegDisplay.unsigned(v):08x}"
	)
	BIN = Format(
		on_exe (lambda v: int(v, 2)),
		lambda v: f"{RegDisplay.unsigned(v):032b}"
	)
	SIGNED = Format(
		on_exe(lambda v: int(v)),
		lambda v: str(v)
	)
	UNSIGNED = Format(
		on_exe(lambda v: int(v)),
		lambda v: str(RegDisplay.unsigned(v))
	)


class Register:
	"""Represents a register in the simulator."""

	def __init__(self, name):
		self.name = name

	def get_name(self):
		"""Get the register name."""
		return self.name

	def format(self, value):
		"""Get formatted value of the register for human display."""
		return str(value)

	def get_format(self):
		"""Get the format used by this register."""
		pass


class RegisterBank:
	"""Represents a register bank."""

	def __init__(self, name, regs):
		self.name = name
		self.regs = regs

	def get_name(self):
		"""Get the name of the register bank."""
		return self.name

	def get_registers(self):
		"""Get the registers of the register bank."""
		return self.regs


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


class DisassemblyException(MessageException):

	def __init__(self, msg):
		MessageException.__init__(self, msg)


class Disassembly:
	"""Represents a disassebly program."""

	def get_code(self):
		"""Return a list of triples (address, bytes, instruction) representing
		the program."""
		pass

	def find_label(self, label):
		"""Find a label and return its address. Return None if the label cannot
		be found."""
		return None

class ApplicationPane:
	"""Interface shared by all components of the application."""

	def on_begin(self, session):
		"""Called when the session is started."""
		pass

	def on_end(self, session):
		"""Called when the project is closed."""
		pass

	def on_project_set(self, session, project):
		"""Called when the project is changed."""
		pass

	def on_sim_start(self, session, sim):
		"""Called when the simulator is started."""
		pass

	def on_sim_stop(self, session, sim):
		"""Called just before the simulator is deleted."""
		pass

	def on_sim_update(self, session, sim):
		"""Called each time the simulator state needs to be updated."""
		pass

	def on_save(self, session, on_done):
		"""Called to save tje sources. Each pane call on_done() when the
		save is done. This allows to support asynchronous for editor saving.
		Default implementation just call on_ready."""
		on_done()

	def on_compiled(self, session):
		"""Called when the compilation is done."""
		pass
