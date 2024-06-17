

from orchid import *
from orchid.mind import *
from orchid import dialog

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
		dialog.Base.__init__(self, page, Label("select a project"), title="Project")
