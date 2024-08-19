"""Pane displaying the registers."""

import orchid as orc
from orchid.table import TableView
from orchid.models import TableModel
from bass import ApplicationPane, RegDisplay


class DisplayRegister:
	"""A displayed register."""

	def __init__(self, reg):
		self.reg = reg
		self.value = None
		self.fmt = reg.get_format()

	def get_name(self):
		"""Get the name of the register."""
		return self.reg.get_name()

	def format(self):
		"""Format the value of the register."""
		if self.value is None:
			return ""
		else:
			return self.fmt.format(self.value)

	def parse(self, text):
		"""Parse the value of the register. Return None in case of
		error."""
		return self.fmt.parse(text)

	def set_value(self, value):
		"""Change the value of the register."""
		self.value = value

	def is_editable(self):
		return self.fmt.parse is not None

	def set_format(self, fmt = None):
		"""Change the display format of the register."""
		if fmt is None:
			self.fmt = self.reg.get_format()
		else:
			self.fmt = fmt


class RegisterModel(TableModel):
	"""Model to display the registers."""

	def __init__(self, regs, pane):
		TableModel.__init__(self)
		self.regs = regs
		self.pane = pane
		self.updating = False

	def get_column_count(self):
		return 2

	def get_row_count(self):
		return len(self.regs)

	def is_edtiable(self, row, col):
		return col == 1

	def get_cell(self, row, column):
		if column == 0:
			return self.regs[row].get_name()
		else:
			return self.regs[row].format()

	def set_cell(self, row, col, val):
		if col == 1:
			self.regs[row].set_value(val)
		TableModel.set_cell(self, row, col, val)


class RegisterPane(TableView, ApplicationPane):
	"""Pane displaying the registers."""

	MODEL = orc.Model(
		"bass.register-pane",
		parent = TableView.MODEL,
		style = """
table.register-pane {
	min-width: 10em;
}

table.register-pane tr td:nth-child(2) {
	min-width: 4em;
}

"""
)

	class SimUpdater(orc.TableObserver):
		"""Update the simulation when """

		def __init__(self, parent):
			self.parent = parent

		def on_cell_set(self, table, row, col, val):
			assert col == 1
			self.parent.sim.set_register(self.parent.regs[row].reg, val)

	def __init__(self):

		def is_editable(row, col):
			return col == 1 \
				and self.sim is not None  \
				and self.regs[row].is_editable()

		def parse(row, col, val):
			return self.regs[row].parse(val)

		# prepare actions
		self.default_action = orc.Action(
			lambda i: self.show_fmt(None), label="Default")
		self.signed_action = orc.Action(
			lambda i: self.show_fmt(RegDisplay.SIGNED), label="Signed")
		self.unsigned_action = orc.Action(
			lambda i: self.show_fmt(RegDisplay.UNSIGNED), label="Unsigned")
		self.hex_action = orc.Action(
			lambda i: self.show_fmt(RegDisplay.HEX), label="Hexadecimal")
		self.bin_action = orc.Action(
			lambda i: self.show_fmt(RegDisplay.BIN), label="Binary")
		toolbar = orc.MenuButton(orc.Menu([
				orc.Button(self.default_action),
				orc.Button(self.signed_action),
				orc.Button(self.unsigned_action),
				orc.Button(self.hex_action),
				orc.Button(self.bin_action)
			]))

		# init parent
		TableView.__init__(self, [], no_header=True, model=self.MODEL,
			format=self.format, parse=parse,
			is_editable=is_editable, context_toolbar=toolbar)
		ApplicationPane.__init__(self)
		self.disable()

		# prepare state
		self.arch = None
		self.regs = None
		self.add_class("register-pane")
		self.changed = []
		self.sim = None
		self.updater = RegisterPane.SimUpdater(self)

	def show_fmt(self, fmt):
		row = self.get_context_row()
		self.regs[row].set_format(fmt)
		self.refresh_cell(row, 1)

	def show_default(self, interface):
		self.show_fmt(None)

	def show_signed(self, interface):
		pass

	def show_unsigned(self, interface):
		pass

	def show_hex(self, interface):
		pass

	def format(self, row, col, val):
		"""Format the value according to the register."""
		if col == 0:
			return val
		else:
			return self.regs[row].format()

	def on_project_set(self, session, project):
		"""Set the current architecture."""
		arch = project.get_arch()
		if arch != self.arch:
			self.arch = arch
			regs = sum(
				(b.get_registers() for b in arch.get_registers()),
				start=[])
			self.regs = [DisplayRegister(r) for r in regs]
			self.set_table_model(RegisterModel(self.regs, self))

	def make_content(self):
		"""Build the content of the component."""
		return None

	def expands_vertical(self):
		return True

	def on_sim_update(self, session, sim):
		changed = []
		self.get_table_model().remove_observer(self.updater)
		for (row, reg) in enumerate(self.regs):
			val = sim.get_register(reg.reg)
			if val != reg.value:
				self.get_table_model().set_cell(row, 1, val)
				changed.append(row)
				if reg not in self.changed:
					self.add_row_class(row, "error-text")
			else:
				if row in self.changed:
					self.remove_row_class(row, "error-text")
		self.get_table_model().add_observer(self.updater)
		self.changed = changed

	def on_sim_start(self, session, sim):
		self.sim = sim
		for (row, reg) in enumerate(self.regs):
			val = sim.get_register(reg.reg)
			self.get_table_model().set_cell(row, 1, val)
		self.get_table_model().add_observer(self.updater)
		self.enable()

	def on_sim_stop(self, session, sim):
		self.disable()
		self.get_table_model().remove_observer(self.updater)
		self.sim = None
		for i in range(len(self.regs)):
			self.get_table_model().set_cell(i, 1, None)
		for i in self.changed:
			self.remove_row_class(i, "error-text")


