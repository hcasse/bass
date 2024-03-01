"""Main module of the BASS."""

class Exception(Exception):

	def __init__(self, msg):
		self.msg = msg

	def __str__(self):
		return self.msg

class Simulator:
	"""Interface to the simulator."""

	def __init__(self, path):
		"""Build the simulator with the given path for the executable."""
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
