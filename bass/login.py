
"""Provides login and project selection dialogs."""

from orchid import \
	HGroup, VGroup, var, Action, ListView, MessageLabel, Field, \
	Button, PasswordField, Label, hspring, matches, if_error, equals, \
	Predicate, EmailField, ListVar, Form, not_null, is_password, Key, is_null
from orchid import dialog
from bass import project_name_pred

class LoginDialog(dialog.Base):

	def __init__(self, session, page):
		self.user = var("", label="User")
		self.pwd = var("", label="Password")
		login = Action(fun=session.login_user, label="Log in")
		anon = Action(fun=session.login_anon, label="Anonymous connect")
		retrieve = Action(fun=session.retrieve_pwd, label="Retrieve")
		register = Action(fun=session.register_user, label="Register")

		content = [
			Form([
				Field(var = self.user, size=20)
					.key(Key.ENTER, lambda: self.page.next_focus()),
				PasswordField(var = self.pwd, size=20)
					.key(Key.ENTER, login),
			]),
			HGroup([hspring(), Button(action=login)]),
			HGroup([Label("Password forgotten?"), hspring(), Button(action=retrieve)]),
		]
		if session.get_application().anon_enable:
			content.append(HGroup([Label("No login"), hspring(), Button(action=anon)]))
		if session.get_application().register_enable:
			content.append(HGroup([hspring(), Button(action=register)]))
		self.msg = MessageLabel("")
		content.append(self.msg)

		dialog.Base.__init__(self, page, VGroup(content), title="Log in")

	def show(self):
		self.msg.clear_message()
		dialog.Base.show(self)

	def error(self, msg):
		self.msg.show_error(msg)


class RegisterDialog(dialog.Base):

	def __init__(self, page, on_cancel, on_apply, config=False):
		"""Build a register dialog with functions on_cancel and on_apply called
		depending on user condition. If configis True, a configuration
		dialog is built."""

		def check_user():
			return not page.get_application().exists_user(~self.user)

		self.user = var("", label="User")
		self.pwd = var("", label="Password")
		self.repwd = var("", label="Re-type password")
		self.email = var("", label="EMail")

		good_pwd = \
			if_error(is_password(self.pwd),
				"Password requires 8 characters: 1 lower, 1 upper, 1 digit, 1 other.") & \
			if_error(equals(self.pwd, self.repwd),
				   "Password and re-typed different!")

		if not config:
			enable = \
				if_error(matches(self.user, "[a-zA-Z0-9_.-]+"),
					"User allowed characters: a-z, A-Z, 0-9, ., _, -.") & \
				if_error(Predicate([self.user], fun=check_user),
					"User already exists!") & \
				good_pwd
		else:
			enable = \
				is_null(self.pwd) | good_pwd
		register = Action(fun=on_apply, enable=enable,
			label="Register" if not config else "Update")
		cancel = Action(fun=on_cancel, label="Cancel")
		self.msg = MessageLabel([enable])

		main = VGroup([
			Form([
				Field(var=self.user, read_only=config),
				PasswordField(var=self.pwd),
				PasswordField(var=self.repwd),
				EmailField(var=self.email),
			]),
			self.msg,
			HGroup([hspring(), Button(cancel), Button(register)]),
		])
		dialog.Base.__init__(self, page, main,
			title="Register" if not config else "Configure user")

	def set_user(self, user):
		"""Set the current user."""
		self.user.set(user.get_name())
		self.pwd.set("")
		self.repwd.set("")
		self.email.set(user.get_email())

	def show(self):
		self.msg.clear_message()
		dialog.Base.show(self)

	def error(self, msg):
		self.msg.show_error(msg)

	def get_password(self):
		"""Get the typed password."""
		return ~self.pwd

	def get_email(self):
		"""Get the typed email."""
		return ~self.email

class SelectDialog(dialog.Base):

	def __init__(self, server, page):
		self.server = server
		self.projects = ListVar([])
		all_templates = server.get_application().get_templates().values()
		actual_templates = [t for t in all_templates if t.is_enabled()]
		self.templates = ListVar(actual_templates)
		self.selected_project = ListVar([])
		self.selected_template = ListVar([])
		self.name = var("")

		def not_exists():
			return not any(~self.name == p.get_name() for p in ~self.projects)
		create_enable = not_null(self.selected_template) \
			& if_error(not_null(self.name), "Name required!") \
			& if_error(Predicate(fun=not_exists, vars=[self.name]), \
				"Project already exists!")
		create_project = Action(
				fun = server.create_project,
				label = "Create",
				enable =  create_enable & project_name_pred(self.name)
			)

		open_enable = not_null(self.selected_project)
		open_project = Action(
				fun = server.open_project,
				label = "Open",
				enable = open_enable
			)

		self.msg = MessageLabel(preds = [create_enable, open_enable])

		main = VGroup([
			HGroup([
				VGroup([
					Label("Open project:"),
					ListView(self.projects, selection=self.selected_project),
					HGroup([hspring(), Button(open_project)])
				]),
				VGroup([
					Label("Create project:"),
					Field(self.name, place_holder="name"),
					Label("Select template:"),
					ListView(self.templates, selection=self.selected_template),
					HGroup([hspring(), Button(create_project)])
				])
			]),
			self.msg
		])

		dialog.Base.__init__(self, page, main, title="Project")
		self.set_style("min-width", "400px")
		self.set_style("min-height", "400px")

	def show(self):
		dialog.Base.show(self)
		self.projects.clear()
		for project in self.server.get_user().get_projects():
			self.projects.append(project)

	def error(self, msg):
		self.msg.show_error(msg)
