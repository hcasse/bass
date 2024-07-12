"""Manage editior pane."""

import orchid as orc
from bass.ace_editor import CodeEditor
from bass.disasm import DisasmPane
from bass import ApplicationPane

class DisasmTab(orc.Tab):
	"""Tab containing disassembly."""

	def __init__(self):
		self.component = DisasmPane()
		self.shown = False
		self.to_disasm = None

	def get_label(self):
		return "Disassembly"

	def get_component(self):
		return self.component

	def set_disasm(self, disasm):
		if self.shown:
			self.component.set_disasm(disasm)
			self.to_disasm = None
		else:
			self.to_disasm = disasm

	def on_show(self):
		self.shown = True
		if self.to_disasm is not None:
			self.component.set_disasm(self.to_disasm)
			self.to_disasm = None

	def on_hide(self):
		self.shown = False


class MyTabEditor(orc.Tab):
	"""ource file editor tab."""

	def __init__(self, label, component, file):
		self.component = component
		self.label = label
		component.source_file = file
		self.file = None

	def get_file(self):
		"""Get the file for the editor."""
		return self.file

	def get_label(self):
		return self.label

	def get_component(self):
		return self.component

	def on_show(self):
		print("Shown", self.label)

	def on_hide(self):
		print("Hidden", self.label)

	def on_release(self):
		print("Released", self.label)


class MyTabConsole(orc.Tab):
	"""Disassembly tab."""
	def __init__(self, label, component):
		self.component = component
		self.label = label

	def get_label(self):
		return self.label

	def get_component(self):
		return self.component

	def on_show(self):
		print("Shown", self.label)

	def on_hide(self):
		print("Hidden", self.label)

	def on_release(self):
		print("Released", self.label)


class EditorPane(orc.TabbedPane, ApplicationPane):

	def __init__(self):
		orc.TabbedPane.__init__(self, [])
		self.editors = []
		self.disasm_tab = None

	def clear(self):
		"""Remove all opened tabs."""
		for tab in self.tabs:
			self.remove(tab)
		self.editors = []

	def open_source(self, file):
		"""Open source file in an editor."""
		tab = MyTabEditor(
			file.get_name(),
			CodeEditor(text = file.load()),
			#orc.Editor(),
			file)
		self.append(tab)
		self.editors.append(tab)

	def on_project_set(self, app, project):
		self.clear()
		for file in project.get_sources():
			self.open_source(file)

	def save_next(self, fun, n=-1, editor=None, content=None):
		"""Iterate for saving all editors."""
		if n >= 0:
			editor.source_file.save(content)
		n += 1
		if n >= len(self.editors):
			fun()
		else:
			def transfer(editor, content):
				self.save_next(fun, n, editor, content)
			self.editors[n].get_component().get_content(transfer)

	def save_all(self, fun):
		"""Save all editors and then call function fun."""
		self.save_next(fun)

	def on_compile(self, session, on_ready):
		self.save_all(on_ready)

	def show_disasm(self, disasm):
		"""Change the current disassembly."""
		if self.disasm_tab is None:
			self.disasm_tab = DisasmTab()
			self.append(self.disasm_tab)
		print("DEBUG: editors disasm =", disasm)
		self.disasm_tab.set_disasm(disasm)
		self.select(self.disasm_tab)

	def update_pc(self, addr):
		"""Update the display according to the current PC."""
		if self.disasm_tab is not None:
			self.disasm_tab.get_component().set_pc(addr)

	def on_sim_start(self, app, sim):
		disasm = app.get_project().get_disassembly()
		print("DEBUG: disasm =", disasm)
		self.show_disasm(disasm)
		self.on_sim_update(app, sim)

	def on_sim_update(self, app, sim):
		pc = sim.get_pc()
		self.update_pc(pc)
