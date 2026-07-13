#
#	BASS is an online training assembly simulator.
#	Copyright (C) 2026 University of Toulouse <hugues.casse@irit.fr>
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

"""Pane for managing I/O component in board simulation."""

from csim.ui import Display
from bass import ApplicationPane

class Pane(Display, ApplicationPane):

	def __init__(self):
		Display.__init__(self)
		self.board = None

	def on_sim_start(self, session, sim):
		if self.board is None:
			self.board = sim.get_board()
			if self.board:
				self.install(self.board)

	def on_sim_update(self, session, sim):
		if self.board:
			self.board.update_input()

	def on_sim_release(self, session, sim):
		self.remove_all()
		self.board = None
