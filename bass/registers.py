"""Pane displaying the registers."""

import orchid as orc
from orchid.table import TableView
from orchid.models import TableModel
from bass import ApplicationPane


class DisplayRegister:
	"""A displayed register."""

	def __init__(self, reg):
		self.reg = reg
		self.format_fun = lambda val: reg.format(val)
		self.value = None

	def get_name(self):
		"""Get the name of the register."""
		return self.reg.get_name()

	def format(self):
		"""Format the value of the register."""
		if self.value is None:
			return ""
		else:
			return self.format_fun(self.value)

	def set_value(self, value):
		"""Change the value of the register."""
		self.value = value


class RegisterModel(TableModel):
	"""Model to display the registers."""

	def __init__(self, regs):
		TableModel.__init__(self)
		self.regs = regs

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

	def is_editable(self, row, col):
		return col == 1 and self.sim is not None

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

	def __init__(self):
		TableView.__init__(self, [], no_header=True, model=self.MODEL)
		ApplicationPane.__init__(self)
		self.arch = None
		self.regs = None
		self.add_class("register-pane")
		self.changed = []

	def on_project_set(self, app, project):
		"""Set the current architecture."""
		arch = project.get_arch()
		if arch != self.arch:
			self.arch = arch
			regs = sum(
				(b.get_registers() for b in arch.get_registers()),
				start=[])
			self.regs = [DisplayRegister(r) for r in regs]
			self.set_table_model(RegisterModel(self.regs))

	def make_content(self):
		"""Build the content of the component."""
		return None

	def expands_vertical(self):
		return True

	def on_sim_update(self, app, sim):
		changed = []
		for (row, reg) in enumerate(self.regs):
			val = sim.get_register(reg.reg)
			if val != reg.value:
				self.get_table_model().set_cell(row, 1, val)
				changed.append(reg)
				if reg not in self.changed:
					self.add_row_class(row, "error-text")
			else:
				if reg in self.changed:
					self.remove_row_class(row, "error-text")
		self.changed = changed

	def on_sim_start(self, app, sim):
		for (row, reg) in enumerate(self.regs):
			val = sim.get_register(reg.reg)
			self.get_table_model().set_cell(row, 1, val)

	def on_sim_stop(self, app, sim):
		for i in range(len(self.regs)):
			self.get_table_model().set_cell(i, 1, None)
