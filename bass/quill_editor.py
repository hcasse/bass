
"""Source editor (current based on Quill)."""


# Good links
#
# https://highlightjs.readthedocs.io/en/latest/readme.html

from orchid import Component, Model

MODEL = Model(
	"base.editor",
	style_paths = [
		"https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.bubble.css",
		"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/atom-one-dark.min.css"
	],
	script_paths = [
		"highlight.min.js",
		#"https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js",
		"https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.js"
	],
	script = """
var quill_list = []

function quill_new(msg) {
	let id = msg['id'];
	console.log(`New quill editor: ${id}`);
	let edit = new Quill(`#${id}`, {
		theme: "bubble",
		modules: {
			toolbar: false,
			history: true,
			clipboard: true,
			syntax: {
				languages: [ {key: "armasm", label: "armasm"} ]
			}
		}
	});
	const component = document.getElementById(msg["id"]);
	component.quill = edit;
}

function quill_get(msg) {
	const component = document.getElementById(msg["id"]);
	const quil = component.quill;
	const text = quil.getText();
	ui_send({ "id": msg["id"], "action": "quill_get", "content": text });
}

console.log("Quill declared!");
""",
	style="""

div.quil {
	padding: 4px;
}

div.quill div.ql-editor {
	padding: 0;
}
"""
)

class Editor(Component):

	def __init__(self, text = ""):
		Component.__init__(self, model=MODEL)
		self.text = text
		self.add_class("quill")
		self.add_class("editor")
		self.fun = None

	def gen(self, out):
		out.write("<div ")
		self.gen_attrs(out)
		out.write("><pre>")
		for line in self.text.split('\n'):
			#out.write('<p>')
			out.write(line)
			out.write('<br/>')
		out.write("</pre></div>")
		self.call("quill_new", {"id": self.get_id()})

	def get_content(self, fun):
		"""Get the content of the edit by calling f(fun, editor)."""
		self.fun = fun
		self.call("quill_get", {"id": self.get_id()})

	def receive(self, msg, handler):
		if msg['action'] == 'quill_get':
			self.fun(self, msg['content'])
		else:
			Component.receive(self, msg, handler)
