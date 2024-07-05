"""Manage editior pane."""

import orchid as orc
from bass.ace_editor import CodeEditor

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


class EditorPane(orc.TabbedPane):

	def __init__(self):
		orc.TabbedPane.__init__(self, [])
		self.editors = []

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

