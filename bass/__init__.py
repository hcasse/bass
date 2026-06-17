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

def find_symbol(path, log=lambda x: None):
	"""Find a symbol from its name. Return the class or None."""
	comps = path.split('.')
	cls = comps[-1]
	path = '.'.join(comps[:-1])
	try:
		mod = importlib.import_module(path)
		return mod.__dict__[cls]
	except (ModuleNotFoundError, KeyError) as e:
		#print(f"DEBUG: find_symbol: {e}")
		log(f"ERROR: {e} looking for {path}")
		return None

class MessageException(Exception):
	"""Base class of exception supporting a message."""

	def __init__(self, msg):
		Exception.__init__(self)
		self.msg = msg

	def __str__(self):
		return self.msg


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
