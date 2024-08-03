
"""Provides login and project selection dialogs."""

from orchid import \
	HGroup, VGroup, var, Action, ListView, MessageLabel, Field, \
	Button, PasswordField, Label, hspring, matches, if_error, equals, \
	Predicate, EmailField, ListVar, Form, not_null, is_password, Key
from orchid import dialog

class LoginDialog(dialog.Base):

	def __init__(self, server, page):
		self.user = var("", label="User")
		self.pwd = var("", label="Password")
		login = Action(fun=server.login_user, label="Log in")
		anon = Action(fun=server.login_anon, label="Anonymous connect")
		retrieve = Action(fun=server.retrieve_pwd, label="Retrieve")
		register = Action(fun=server.register_user, label="Register")

		self.msg = MessageLabel("")
		main = VGroup([
				Form([
					Field(var = self.user, size=20)
						.key(Key.ENTER, lambda: self.page.next_focus()),
					PasswordField(var = self.pwd, size=20)
						.key(Key.ENTER, login),
				]),
				HGroup([hspring(), Button(action=login)]),
				HGroup([Label("Password forgotten?"), hspring(), Button(action=retrieve)]),
				HGroup([Label("No login"), hspring(), Button(action=anon)]),
				HGroup([hspring(), Button(action=register)]),
				self.msg
			])
		dialog.Base.__init__(self, page, main, title="Log in")

	def show(self):
		self.msg.clear_message()
		dialog.Base.show(self)

	def error(self, msg):
		self.msg.show_error(msg)


class RegisterDialog(dialog.Base):

	def __init__(self, server, page):
		self.server = server
		self.user = var("", label="User")
		self.pwd = var("", label="Password")
		self.repwd = var("", label="Re-type password")
		self.email = var("", label="EMail")

		enable = \
			if_error(matches(self.user, "[a-zA-Z0-9_.-]+"),
				"User allowed characters: a-z, A-Z, 0-9, ., _, -.") & \
			if_error(is_password(self.pwd),
				"Password requires 8 characters: 1 lower, 1 upper, 1 digit, 1 other.") & \
			if_error(Predicate([self.user], fun=self.check_user),
				"User already exists!") & \
			if_error(equals(self.pwd, self.repwd),
				   "Password and re-typed different!")
		register = Action(fun=server.create_user, enable=enable, label="Register")
		cancel = Action(fun=server.cancel_user, label="Cancel")
		self.msg = MessageLabel([enable])

		main = VGroup([
			Form([
				Field(var=self.user),
				PasswordField(var=self.pwd),
				PasswordField(var=self.repwd),
				EmailField(var=self.email),
			]),
			self.msg,
			HGroup([hspring(), Button(cancel), Button(register)]),
		])
		dialog.Base.__init__(self, page, main, title="Register")

	def show(self):
		self.msg.clear_message()
		dialog.Base.show(self)

	def check_user(self):
		return not self.server.get_application().exists_user(~self.user)

	def error(self, msg):
		self.msg.show_error(msg)


class SelectDialog(dialog.Base):

	def __init__(self, server, page):
		self.projects = ListVar(server.get_user().get_projects())
		self.templates = ListVar(list(server.get_application().get_templates().values()))
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
				enable =  create_enable
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


	def error(self, msg):
		self.msg.show_error(msg)
