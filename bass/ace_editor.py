
"""Source editor (current based on ACE)."""


# Good links
#
# https://ace.c9.io/#nav=embedding

from orchid import Component, Model

MODEL = Model(
	"base.editor",
	#script_paths = ["ace/ace.js"],
	script_paths = [
		"https://cdn.jsdelivr.net/npm/ace-builds@1.35.0/src-min-noconflict/ace.js"
	],
	script = """
function ace_new(msg) {
	const id = msg['id'];
	const component = document.getElementById(id);
	const editor = ace.edit(id)
    editor.setTheme("ace/theme/clouds");
    editor.session.setMode("ace/mode/assembly_arm32");	component.ace_editor = editor;
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
}
"""
)

class CodeEditor(Component):

	def __init__(self, text = ""):
		Component.__init__(self, model=MODEL)
		self.text = text
		self.add_class("editor")
		self.generated = False
		self.fun = None
		#self.set_attr("position", "relative")

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
			self.fun(self, msg['content'])
		else:
			Component.receive(self, msg, handler)

