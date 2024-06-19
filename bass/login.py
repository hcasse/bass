

from orchid import *
from orchid.mind import *
from orchid import dialog
from orchid.models import ListVar
from orchid.list import *

class LoginDialog(dialog.Base):

	def __init__(self, server, page):
		self.user = Var("", label="User")
		self.pwd = Var("", label="Password")
		login = Action(fun=server.login_user, label="Log in")
		anon = Action(fun=server.login_anon, label="Anonymous connect")
		retrieve = Action(fun=server.retrieve_pwd, label="Retrieve")
		register = Action(fun=server.register_user, label="Register")

		self.msg = MessageLabel("")
		main = VGroup([
				Form([
					Field(var = self.user, size=20),
					PasswordField(var = self.pwd, size=20),
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
		self.user = Var("", label="User")
		self.pwd = Var("", label="Password")
		self.repwd = Var("", label="Re-type password")
		self.email = Var("", label="EMail")
		self.msg = MessageLabel("")

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

		main = VGroup([
			Form([
				Field(var=self.user),
				PasswordField(var=self.pwd),
				PasswordField(var=self.repwd),
				EmailField(var=self.email)
			]),
			HGroup([hspring(), Button(cancel), Button(register)]),
			self.msg
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
		self.name = Var("")
		self.msg = MessageLabel("")

		create_project = Action(
				fun = server.create_project,
				label = "Create",
				enable =  not_null(self.selected_template) \
						& if_error(not_null(self.name), "Name required!") \
						& if_error(Predicate(fun=self.not_exists), "Project already exists!")
			)
		open_project = Action(
				fun = server.open_project,
				label = "Open",
				enable = not_null(self.selected_project)
			)

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

	def not_exists(self):
		print("DEBUG:", ~self.name, "in", ~self.projects, "=", ~self.name not in ~self.projects)
		return ~self.name not in ~self.projects

	def error(self, msg):
		self.msg.show_error(msg)
