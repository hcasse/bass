
"""Source editor (current based on ACE)."""


# Good links
#
# https://ace.c9.io/#nav=embedding

from orchid import VGroup, Model, Component, ButtonBar, Button, Action, \
	IconType, Icon, HSpace
import bass

MODEL = Model(
	"base.editor",
	script_paths = ["ace/ace.js"],
	#script_paths = [
	#	"test.js",
	#	"https://cdn.jsdelivr.net/npm/ace-builds@1.35.0/src-min-noconflict/ace.js"
	#],
	script = """
function ace_new(msg) {
	const id = msg['id'];
	const component = document.getElementById(id);
	const editor = ace.edit(id)
    editor.setTheme("ace/theme/clouds");
    editor.session.setMode("ace/mode/assembly_arm32");
    component.ace_editor = editor;
	editor.setOptions({
	});
}

function ace_get(msg) {
	const id = msg['id'];
	const component = document.getElementById(id);
	const editor = component.ace_editor;
	const content = editor.getValue();
	ui_send({ "id": msg["id"], "action": "ace_get", "content": content });
}

function ace_set(msg) {
	const id = msg['id'];
	const component = document.getElementById(id);
	const editor = component.ace_editor;
	editor.setValue(msg["content"]);
	editor.clearSelection();
	editor.session.getUndoManager().reset();
}

function ace_undo(msg) {
	const component = document.getElementById(msg.id);
	const editor = component.ace_editor;
	editor.undo();
}

function ace_redo(msg) {
	const component = document.getElementById(msg.id);
	const editor = component.ace_editor;
	editor.redo();
}

function ace_copy(msg) {
	const component = document.getElementById(msg.id);
	const editor = component.ace_editor;
	let text = editor.getCopyText();
	navigator.clipboard.writeText(text);
}

function ace_cut(msg) {
	const component = document.getElementById(msg.id);
	const editor = component.ace_editor;
	let text = editor.getCopyText();
	editor.insert("");
	navigator.clipboard.writeText(text);
}

function ace_paste(msg) {
	const component = document.getElementById(msg.id);
	const editor = component.ace_editor;
	const data = navigator.clipboard.read();
	for(let i = 0; i < data.length; i++)
		if(data[i].types.includes("text/plain"))
			editor.session.insert(editor.getCursorPosition(), data[i].getType("text/plain"));
}

function ace_focus(msg) {
	const component = document.getElementById(msg.id);
	const editor = component.ace_editor;
	editor.focus();
}

function ace_find(msg) {
	const component = document.getElementById(msg.id);
	const editor = component.ace_editor;
	editor.execCommand('find');
}

function ace_replace(msg) {
	const component = document.getElementById(msg.id);
	const editor = component.ace_editor;
	editor.execCommand('replace');
}
"""
)

class Editor(Component):
	"""The editor itself."""

	def __init__(self, text = ""):
		Component.__init__(self, model=MODEL)
		self.text = text
		self.add_class("editor")
		self.generated = False
		self.fun = None

	def expands_horizontal(self):
		return True

	def expands_vertical(self):
		return True

	def gen(self, out):
		out.write("<div ")
		self.gen_attrs(out)
		out.write('>')
		out.write("</div>")
		self.call("ace_new", {"id": self.get_id()})
		self.call("ace_set", {"id": self.get_id(), "content": self.text})
		self.generated = True

	def get_content(self, fun):
		"""Get the content of the edit by calling f(fun, editor)."""
		self.fun = fun
		self.call("ace_get", {"id": self.get_id()})

	def receive(self, msg, handler):
		if msg['action'] == 'ace_get':
			self.fun(msg['content'])
		else:
			VGroup.receive(self, msg, handler)

	def undo(self, interface):
		"""Perform undo operation."""
		self.call("ace_undo", {"id": self.get_id()})

	def redo(self, interface):
		"""Perform redo operation."""
		self.call("ace_redo", {"id": self.get_id()})

	def copy(self, interface):
		"""Perform copy operation."""
		self.call("ace_copy", {"id": self.get_id()})

	def cut(self, interface):
		"""Perform cut operation."""
		self.call("ace_cut", {"id": self.get_id()})

	def paste(self, interface):
		"""Perform copy operation."""
		self.call("ace_paste", {"id": self.get_id()})

	def grab_focus(self, **args):
		self.call("ace_focus", {"id": self.get_id()})

	def find(self, interface):
		"""Display find command."""
		self.call("ace_find", {"id": self.get_id()})

	def replace(self, interface):
		"""Display the replace command."""
		self.call("ace_replace", {"id": self.get_id()})


class CodeEditor(VGroup, bass.ApplicationPane):

	def __init__(self, file):

		# make editor
		self.file = file
		text = file.load()
		self.editor = Editor(text)

		# make button bar
		save_action = Action(self.save, icon=Icon(IconType.SAVE),
			help="Save the source file.")
		undo_action = Action(self.editor.undo, icon=Icon(IconType.UNDO),
			help="Undo the last actions.")
		redo_action = Action(self.editor.redo, icon=Icon(IconType.REDO),
			help="Redo undone actions.")
		copy_action = Action(self.editor.copy, icon=Icon(IconType.COPY),
			help="Copy current text to clipboard.")
		cut_action = Action(self.editor.cut, icon=Icon(IconType.CUT),
			help="Cut current text and store it to clipboard.")
		paste_action = Action(self.editor.paste, icon=Icon(IconType.PASTE),
			help="Paste current text from clipboard.")
		find_action = Action(self.editor.find, icon=Icon(IconType.FIND),
			help="Find word in text.")
		replace_action = Action(self.editor.replace, icon=Icon(IconType.REPLACE),
			help="Search and replace.")

		VGroup.__init__(self, [
			ButtonBar([
				Button(save_action),
				Button(undo_action),
				Button(redo_action),
				HSpace(),
				Button(cut_action),
				Button(copy_action),
				Button(paste_action),
				HSpace(),
				Button(find_action),
				Button(replace_action)
			]),
			self.editor
		], model=MODEL)

	def get_content(self, fun):
		"""Get the content of the edit by calling f(fun, editor)."""
		self.editor.get_content(fun)

	def on_save(self, session, on_done):
		def save(content):
			self.file.save(content)
			on_done()
		self.get_content(save)

	def save(self, interface):
		"""Save the current file."""
		self.on_save(None, lambda: None)
