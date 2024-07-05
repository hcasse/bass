var quill_list = []

function quill_new(msg) {
	let id = msg['id'];
	let edit = new Quill("#{id}", {
		theme: "snow"
	});
	console.log("New quill editor: {id}");
}
