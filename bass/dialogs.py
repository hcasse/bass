"""Other dialog management"""


from orchid import \
	HGroup, VGroup, Var, Action, Field, Key, hspring, Button, Predicate, \
		MessageLabel
from orchid import dialog, MessageType
from bass import project_name_pred

class RenameDialog(dialog.Base):
	"""An action tor rename the project."""

	def __init__(self, session, rename):
		"""Build the dialog. Session is the session with current project to be
		renamed. Rename is the function to call to rename (name as argument).
		In case of cancel, the dialog is just hidden."""
		self.session = session
		self.name = Var("", label="Name")

		def unique():
			return all(~self.name != project.get_name()
				for project in session.get_user().get_projects())

		cancel_action = Action(fun=lambda _: self.hide(), label="Cancel")
		rename_action = Action(fun=lambda _: rename(~self.name),
			label="Rename",
			enable=Predicate([self.name], unique) & \
				project_name_pred(self.name))

		self.msg = MessageLabel("")
		main = VGroup([
				Field(var = self.name, size=20)
					.key(Key.ENTER, lambda: rename()),
				HGroup([
					hspring(),
					Button(cancel_action),
					Button(rename_action)
				]),
				self.msg
			])
		dialog.Base.__init__(self, session.get_page(), main, title="Rename project")

	def on_show(self):
		dialog.Base.on_show(self)
		self.msg.clear_message()
		self.name.set(self.session.get_project().get_name())

	def error(self, msg):
		self.msg.show_error(msg)


class DeleteDialog(dialog.Answer):
	"""Dialog asking the user to validate deletion of current project."""

	def __init__(self, session, delete):
		"""Build the dialog. Delete function is called is case of validation."""

		def on_close(dialog, answer):
			self.hide()
			if answer == 0:
				delete()

		dialog.Answer.__init__(
			self,
			session.get_page(),
			f"Do you want to delete {session.get_project().get_name()}?",
			buttons = ["Delete", "Cancel"],
			title="Project Deletion",
			on_close=on_close
		)

		self.get_button(0).set_style("color", "red")


class ErrorDialog(dialog.Message):
	"""Dialog to display an error."""

	def __init__(self, page):
		dialog.Message.__init__(self, page, "", title="Error", type=MessageType.ERROR)

	def show_error(self, message):
		self.set_message(message)
		self.show()


