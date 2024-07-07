"""Main module of the BASS."""

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


class Simulator:
	"""Interface to the simulator."""

	def __init__(self, path):
		"""Build the simulator with the given path for the executable.
		If there is an error, raises a SimException."""
		self.exec_path = path

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

	def step(self):
		"""Execute the current instruction and stop."""
		pass


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
