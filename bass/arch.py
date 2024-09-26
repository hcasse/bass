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

import bass

class Register(bass.Register):
	"""Simple decimal register displat."""

	def __init__(self, name, bank, index, format=bass.RegDisplay.SIGNED):
		bass.Register.__init__(self, name)
		self.bank = bank
		self.index = index
		self.fmt = format

	def format(self, value):
		return self.fmt.format(value)

	def get_format(self):
		return self.fmt


class AddrRegister(Register):
	"""Register containing an address."""

	def __init__(self, name, bank, index):
		Register.__init__(self, name, bank, index, bass.RegDisplay.HEX)

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

	FORMAT = bass.Format(None, do_format, custom = True)

	def __init__(self, name, bank, index):
		Register.__init__(self, name, bank, index, self.FORMAT)
