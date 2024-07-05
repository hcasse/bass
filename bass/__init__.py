"""Main module of the BASS."""

class SimException(Exception):
	"""Exception thrown when an error arises in the simulation."""

	def __init__(self, msg):
		Exception.__init__(self)
		self.msg = msg

	def __str__(self):
		return self.msg

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
