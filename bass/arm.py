"""ARM configuration for bass."""

import os.path

import bass
import armgliss as arm

DATADIR = os.path.abspath("data")
CC = "arm-linux-gnueabihf-gcc"
CFLAGS = "-g"
LDFLAGS = "-static -nostartfiles"
INITIAL_SOURCE ="""
	.global	_start

_start:


_exit:
	b	_exit
"""
EXEC_EXT = "elf"

CC_COMMAND = "%s %s -o '%%s' '%%s' %s" % (CC, CFLAGS, LDFLAGS)


class Simulator(bass.Simulator):

	def __init__(self, path):
		bass.Simulator.__init__(self, path)
		self.labels = None
		self.breaks = []
		self.pf = None
		self.loader = None
		self.state = None
		self.sim = None

		# load the executable
		self.pf = arm.new_platform()
		self.loader = arm.loader_open(path)
		if self.loader == None:
			raise Bass.Exception("cannot load %s" % path)
		arm.loader_load(self.loader, self.pf);
		self.start = arm.loader_start(self.loader)

		# prepare the simulator
		self.state = arm.new_state(self.pf)
		self.sim = arm.new_sim(self.state, self.start, 0)

	def release(self):
		if self.sim != None:
			arm.delete_sim(self.sim)
		if self.loader != None:
			arm.loader_close(self.loader)

	def get_label(self, name):
		if labels == None:
			self.labels = {}
			for i in range(0, arm.loader_count_syms(self.loader)):
				sym = arm.loader_sym(self.loader, i)
				self.labels[sym[0]] = sym[1]
		try:
			return self.labels[name]
		except KeyError:
			return None

	def set_break(self, addr):
		self.breaks.append(addr)


def load(path):
	return Simulator(path)
	
