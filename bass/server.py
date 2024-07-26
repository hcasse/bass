#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""BASS Application."""

import argparse
from datetime import datetime
import os
import os.path
import re
import sys
import time

import Orchid.orchid as orc
from Orchid.orchid import popup
from Orchid.orchid import dialog

import bass
from bass.ace_editor import CodeEditor
from bass.disasm import DisasmPane
from bass.login import LoginDialog, RegisterDialog, SelectDialog
from bass.data import Project, Template, User, DataException
from bass.registers import RegisterPane
from bass.memory import MemoryPane


LINE_RE = re.compile(r"^([^\.]+\.[^:]:[0-9]+:).*$")

# debug configuration
DEBUG = False
DEBUG_USER = None
DEBUG_PROJECT = None


class EditorTab(CodeEditor, bass.ApplicationPane):
	"""Class for code edition (embed interaction with session)."""

	def __init__(self, file):
		self.file = file
		text = file.load()
		CodeEditor.__init__(self, text=text)

	def on_save(self, session, on_done):
		def save(self, content):
			self.file.save(content)
			on_done()
		self.get_content(save)


class Session(orc.Session):

	AUTO_BP = { "main", "_exit" }

	def __init__(self, app, man):
		orc.Session.__init__(self, app, man)

		# get configuration
		self.sim_freq = app.get_config("sim_freq", 5)

		# application state
		self.user = None
		self.project = None
		self.sim = None
		self.compiled = orc.Var(False)
		self.started = orc.Var(False)
		self.running = orc.Var(False)
		self.ready_count = 0
		self.quantum_inst = None
		self.quantum_period = 1000 / self.sim_freq
		self.date = orc.Var(None, orc.Types.INT)
		self.sim_timeout = orc.Var(False,
			icon=orc.Icon(orc.IconType.STOPWATCH, color="green"))
		self.timeout_icon = orc.Icon(orc.IconType.STOPWATCH, color="red")
		self.breakpoints = orc.SetVar(set(), item_type=int)
		self.stop_on = self.is_breakpoint
		self.bp_to_remove = set()
		self.current_addr = orc.Var(None, type=int)

		# compilation and simulation actions
		self.start_icon = orc.Icon(orc.IconType.PLAY, color="green")
		self.stop_icon = orc.Icon(orc.IconType.STOP, color="red")
		self.compile_action = orc.Action(self.compile,
			icon=orc.Icon(orc.IconType.CHECK), help="Compile the project.")
		self.playstop_action = orc.Action(self.playstop, enable=self.compiled,
			icon=self.start_icon,
			help="Play/stop the simulation.")
		paused = self.started & orc.not_(self.running)
		self.step_action = orc.Action(self.step, enable=paused,
			icon=orc.Icon(orc.IconType.BRACES), help="Execute one instruction.")
		self.step_over_action = orc.Action(self.step_over, enable=paused,
			icon=orc.Icon("!braces-asterisk"),
			help="Execution one instruction passing over subprogram call.")
		self.run_to_action = orc.Action(self.run_to,
			enable=paused & orc.not_null(self.current_addr),
			icon=orc.Icon(orc.IconType.SKIP_FORWARD), help="Run to current position.")
		self.go_on_action = orc.Action(self.go_on, enable=paused,
			icon=orc.Icon(orc.IconType.FAST_FORWARD), help="Go on execution.")
		self.pause_action = orc.Action(self.pause, enable=self.running,
			icon=orc.Icon(orc.IconType.PAUSE), help="Pause the execution")
		self.reset_action = orc.Action(self.reset, enable=paused,
			icon=orc.Icon(orc.IconType.RESET), help="Reset the simulation.")

		self.open_new_project_action = orc.Action(self.open_new_project,
			label="Open/New", help="Close current project and open/create another.")
		self.rename_project_action = orc.Action(self.rename_project,
			label="Rename", help="Rename the current project.")
		self.delete_project_action = orc.Action(self.delete_project,
			label="Delete", help="Delete the current project.")

		self.config_user_action = orc.Action(self.config_user,
			label="Configure", help="Change user configuration.")
		self.logout_action = orc.Action(self.logout,
			label="Logout", help="Logout from this session.")

		# UI
		self.panes = []
		self.page = None
		self.user_label = None
		self.project_label = None
		self.console = None
		self.sim_timer = None
		self.timeout_button = None
		self.editors = None
		self.disasm = None
		self.last_tab = None
		self.addons = None

		# dialog
		self.login_dialog = None
		self.register_dialog = None
		self.select_dialog = None

	def get_current_addr(self):
		"""Get the variable containing the current address."""
		return self.current_addr

	def get_breakpoints(self):
		"""Return the variable containing the set of breakpoints."""
		return self.breakpoints

	def get_user(self):
		"""Get the current user."""
		return self.user

	def get_project(self):
		"""Get the current project."""
		return self.project

	def update_sim_display(self):
		"""Udpdate the display according to the current simulator state."""
		for pane in self.panes:
			pane.on_sim_update(self, self.sim)
		self.date.set(self.sim.get_date())

	def is_breakpoint(self, pc):
		"""Test if the given PC is a breakpoint."""
		return pc in ~self.breakpoints

	def execute_quantum(self):
		timeout = time.time() + self.quantum_period / 1000
		for _ in range(self.quantum_inst):
			self.sim.step()
			if time.time() >= timeout:
				self.sim_timeout.set(False)
				break
			pc = self.sim.get_pc()
			if self.stop_on(pc):
				self.complete_quantum()
				return
		self.sim_timeout.set(True)
		self.update_sim_display()

	def complete_quantum(self):
		self.sim_timer.stop()
		self.running.set(False)
		self.sim_timeout.set(False)
		self.update_sim_display()
		self.stop_on = self.is_breakpoint

	def start_sim(self):
		"""Start the simulation."""

		# start the simulator
		try:
			self.sim = self.get_project().new_sim()
		except bass.SimException as e:
			self.console.append(orc.text(orc.ERROR, f"ERROR:{e}"))
			return

		# prepare simulation
		self.quantum_inst = int(self.sim.get_frequency() / self.sim_freq)
		self.started.set(True)
		self.timeout_button.enable()
		self.date.set(0)
		self.console.append(orc.text(orc.INFO, "Start simulation."))

		# update panes
		for pane in self.panes:
			pane.on_sim_start(self, self.sim)
		self.last_tab = self.editors.get_select()
		self.editors.select(self.disasm)
		self.playstop_action.set_icon(self.stop_icon)

	def stop_sim(self):
		"""Stop the current simulation."""

		# stop execution
		if ~self.running:
			self.pause(None)

		# stop the simulator
		self.sim.release()
		self.sim = None
		self.started.set(False)
		self.console.append(orc.text(orc.INFO, "Stop simulation."))
		self.timeout_button.disable()
		self.date.set(None)
		self.sim_timeout.set(False)

		# update panes
		for pane in self.panes:
			pane.on_sim_stop(self, self.sim)
		self.editors.select(self.last_tab)
		self.playstop_action.set_icon(self.start_icon)

	def playstop(self, interface):
		if self.sim is not None:
			self.stop_sim()
		else:
			self.start_sim()

	def step(self, interface):
		"""Perform the execution of one instruction."""
		self.sim.step()
		self.update_sim_display()

	def step_over(self, interface):
		"""Perform the execution of the current line."""
		addr = self.sim.next_pc()
		def is_end(pc):
			return pc == addr
		self.stop_on = is_end
		self.go_on(interface)

	def run_to(self, interface):
		"""Run to the current cursor position."""
		if ~self.current_addr is not None:
			def is_end(pc):
				return ~self.current_addr == pc
			self.stop_on = is_end
			self.go_on(interface)

	def go_on(self, interface):
		"""Go on with the execution."""
		self.running.set(True)
		self.sim_timeout.set(True)
		self.sim_timer.start()

	def pause(self, interface):
		"""Pause the execution."""
		self.complete_quantum()

	def reset(self, interface):
		"""Reset the simulation."""
		self.sim.reset()
		self.update_sim_display()

	def save_all(self, on_done):
		"""Save all editors and call function on_done() when it is completed.
		Other parameters must not be used."""
		self.ready_count = len(self.panes)
		def on_ready():
			self.ready_count -= 1
			if self.ready_count == 0:
				on_done()
		for pane in self.panes:
			pane.on_save(self, on_ready)

	def compile(self, interface):
		"""Start compilation action by saving all editors."""
		self.save_all(self.then_compile)

	def then_compile(self):
		"""Whan all is saved, finally perform the compilation."""
		self.console.clear()
		self.console.append("<b>Compiling...</b>")
		(result, output, error) = self.project.compile()
		for line in output.split("\n"):
			self.print_line(line)
		for line in error.split("\n"):
			self.print_line(line)
		if result != 0:
			self.console.append(orc.text(orc.FAILED, "FAILED..."))
			self.compiled.set(False)
		else:

			# record success
			self.console.append(orc.text(orc.SUCCESS, "SUCCESS!"))
			self.compiled.set(True)
			self.current_addr.set(None)

			# alert panes
			for pane in self.panes:
				pane.on_compiled(self)

			# put default breakpoints
			for addr in self.bp_to_remove:
				self.breakpoints.remove(addr)
			self.bp_to_remove = set()
			disasm = self.project.get_disasm()
			for lab in ["main", "_exit"]:
				addr = disasm.find_label(lab)
				if addr is not None:
					self.breakpoints.add(addr)
					self.bp_to_remove.add(addr)


	def print_line(self, line):
		m = LINE_RE.match(line)
		if m is not None:
			p = m.end(1)
			line = orc.text(orc.INFO, line[:p]) + line[p:]
		self.console.append(line)

	def help(self):
		pass

	def about(self):
		d=dialog.About(self.page)
		d.show()

	def eventResetButton(self):
		#self.initRegister()
		print("Button reset appuye")

	def menuImport(self):
		pass

	def menuSave(self):
		pass

	def menuNew(self):
		pass

	def edit_user(self, interface):
		"""Called to edit the buser."""
		pass

	def make_menu(self):
		return popup.MenuButton(
			popup.Menu([
				orc.Button("Importer", on_click=self.menuImport),
				orc.Button("Telecharger", on_click=self.menuSave),
				orc.Button("Nouveau fichier", on_click=self.menuNew)
			])
		)

	def get_index(self):

		# prepare user display
		self.user_label = orc.Label("")
		self.user_label.set_style("min-width", "8em")
		user_menu = orc.MenuButton(
			orc.Menu([
				orc.Button(self.config_user_action),
				orc.Button(self.logout_action)
			]),
			image = orc.Icon(orc.IconType.PERSON)
		)

		# prepare project display
		self.project_label = orc.Label("")
		self.project_label.set_style("min-width", "8em")
		project_menu = orc.MenuButton(
			orc.Menu([
				orc.Button(self.open_new_project_action),
				orc.Button(self.rename_project_action),
				orc.Button(self.delete_project_action)
			]),
			image = orc.Icon(orc.IconType.PROJECT)
		)

		# generate the page
		self.console = orc.Console(init = "<b>Welcome to BASS!</b>\n")
		#self.memory_pane = orc.Console(init = "Memory")
		register_pane = RegisterPane().set_weight(1)
		self.panes.append(register_pane)
		self.editors = orc.TabbedPane()
		#self.panes.append(editor_pane)
		memory_pane = MemoryPane()
		self.panes.append(memory_pane)
		self.addons = orc.TabbedPane([("Memory", memory_pane)])
		editor_group = orc.HGroup([
			self.editors,
			self.addons
		])
		editor_group.weight = 3
		self.console.weight = 1
		self.timeout_button = orc.TwoStateButton(self.sim_timeout,
			icon2=self.timeout_icon)
		self.timeout_button.disable()
		self.page = orc.Page(
			orc.VGroup([
				orc.Header("BASS", [
					project_menu, self.project_label,
					user_menu, self.user_label,
				]),
				orc.ToolBar([
					orc.Button(self.compile_action),
					orc.Button(self.playstop_action),
					orc.Button(self.step_action),
					orc.Button(self.step_over_action),
					orc.Button(self.run_to_action),
					orc.Button(self.go_on_action),
					orc.Button(self.pause_action),
					orc.Button(self.reset_action),
					orc.Spring(hexpand = True),
					orc.Button(orc.Icon(orc.IconType.HELP), on_click=self.help),
					orc.Button(orc.Icon(orc.IconType.ABOUT), on_click=self.about)
				]),
				orc.HGroup([
					register_pane,
					orc.VGroup([
						editor_group,
						self.console
					]).set_weight(4)
				]),
				orc.StatusBar([
					orc.hspring(),
					orc.Field(self.date, read_only=True, place_holder="date"),
					self.timeout_button
				])
			]),
			app = self.get_application()
		)
		self.sim_timer = orc.Timer(self.page, self.execute_quantum,
			period=self.quantum_period)

		# start session
		for pane in self.panes:
			pane.on_begin(self)

		# prepare dialogs
		self.login_dialog = LoginDialog(self, self.page)
		self.register_dialog = None
		self.select_dialog = None

		# perform connection
		if DEBUG:
			self.get_application().log("INFO: entering debugging mode!")

		if not DEBUG_USER:
			self.login_dialog.show()
		else:

			# log user
			user = User(self.get_application(), DEBUG_USER)
			user.load()
			self.setup_user(user)

			# open the project
			if DEBUG_PROJECT is None:
				self.select_project()
			else:
				done = False
				for project in user.get_projects():

					if project.get_name() == DEBUG_PROJECT:
						project.load()
						self.setup_project(project)
						done = True
						break
				if not done:
					self.get_application().log(f"cannot open project {DEBUG_PROJECT}")
					sys.exit(1)

		return self.page


	# project management

	def setup_project(self, project):
		"""Setup the project in the main window."""

		# display project
		self.project = project
		self.project_label.set_text(project.get_name())

		# setup editors
		for file in project.get_sources():
			editor = EditorTab(file)
			self.editors.append_tab(editor,	label=file.get_name())
			self.panes.append(editor)
			editor.on_begin(self)
		self.disasm = DisasmPane()
		self.editors.append_tab(self.disasm, label="Disassembly")
		self.panes.append(self.disasm)
		self.disasm.on_begin(self)

		# setup panes
		for pane in self.panes:
			pane.on_project_set(self, project)
		self.compiled.set(False)

	def cleanup_project(self, after):
		"""Cleanup a project before closing. After is the function that
		is called after the cleanup (no argument)."""
		if ~self.started:
			self.stop_sim()
		def after_save():
			for pane in self.panes:
				pane.on_end(self)
			while self.editors.get_tabs():
				self.panes.remove(self.editors.get_tabs()[0].get_component())
				self.editors.remove_tab(0)
			self.disasm = None
			self.project = None
			after()
		self.save_all(after_save)

	def open_new_project(self, interface):
		"""Implements action open/new."""
		def after():
			self.select_project()
		self.cleanup_project(after)

	def rename_project(self, interface):
		pass

	def delete_project(self, interface):
		pass


	# user management

	def setup_user(self, user):
		"""Set the user in the main window."""
		self.user = user
		self.user_label.set_text(user.get_name())

	def login_user(self, console):
		""" Try to log-in a user reacting to the login dialog."""
		name = ~self.login_dialog.user
		pwd = ~self.login_dialog.pwd
		if not self.get_application().check_password(name, pwd):
			self.login_dialog.error("Log-in error!")
		else:
			user = User(self.get_application(), name)
			try:
				user.load()
				self.setup_user(user)
				self.login_dialog.hide()
				self.select_project()
			except DataException as e:
				self.login_dialog.error(f"cannot log to {name}: {e}")


	def config_user(self, interface):
		"""Change configuration of the user."""
		pass

	def logout(self, interface):
		"""Stop the current session."""
		def after():
			self.user = None
			self.login_dialog.show()
		self.cleanup_project(after)

	def register_user(self, console):
		self.login_dialog.hide()
		if self.register_dialog is None:
			self.register_dialog = RegisterDialog(self, self.page)
		self.register_dialog.show()

	def login_anon(self, console):
		i = 0
		while True:
			name = f"anon-{i}"
			user_dir = os.path.join(self.get_application().get_data_dir(), name)
			if not os.path.exists(user_dir):
				break
			i += 1
		user = User(self.get_application(), name)
		try:
			user.create()
			self.setup_user(self.user)
			self.login_dialog.hide()
			self.select_project()
		except DataException as e:
			self.login_dialog.error(e)

	def retrieve_pwd(self, console):
		pass

	def cancel_user(self, console):
		"""Registration cancelled."""
		self.register_dialog.hide()
		self.login_dialog.show()

	def create_user(self, console):
		"""Register a new user after dialog edition."""
		name = ~self.register_dialog.user
		if self.get_application().exists_user(name):
			self.register_dialog.user.update_observers()
			return
		user = User(self.get_application(), name, email=~self.register_dialog.email)
		try:
			user.create()
			self.get_application().add_password(name, ~self.register_dialog.pwd)
			self.setup_user(user)
			self.register_dialog.hide()
			self.select_project()
		except DataException as e:
			self.register_dialog.error(str(e))

	def select_project(self):
		"""Open the dialog to select a project or create a new one."""
		if self.select_dialog is None:
			self.select_dialog = SelectDialog(self, self.page)
		self.select_dialog.show()

	def create_project(self, interface):
		"""Create a project after selection dialog."""
		template = self.select_dialog.templates[self.select_dialog.selected_template[0]]
		name = ~self.select_dialog.name
		project = Project(self.user, name, template)
		try:
			project.create()
			self.select_dialog.hide()
			self.setup_project(project)
			self.user.add_project(project)
			self.user.save()
		except DataException as e:
			self.select_dialog.error(str(e))

	def open_project(self, interface):
		"""Open an existing project."""
		project = self.select_dialog.projects[self.select_dialog.selected_project[0]]
		try:
			project.load()
			self.select_dialog.hide()
			self.setup_project(project)
		except DataException as e:
			self.select_dialog.error(f"cannot open {project.get_name()} project: {e}")


class Application(orc.Application):
	"""BASS Application"""
	def __init__(self):
		orc.Application.__init__(self,
			name = "bass",
			authors = ['H. Cassé', "W. McJ. Joseph", "C. Jéré"],
			version="1.0.1",
			description = "Machine level simulator.",
			license = "GPL v3",
			copyright = "Copyright (c) 2023, University of Toulouse 3",
			website="https://github.com/hcasse/bass"
		)

		self.data_dir = os.path.join(os.getcwd(), "data")
		self.base_dir = os.path.dirname(__file__)

		# load passwords
		self.pwd_path = os.path.join(self.data_dir, "passwords.txt")
		self.load_passwords()

		# load templates
		self.template_path = os.path.join(self.base_dir, "templates")
		self.load_templates()

	def log(self , msg):
		"""Log a message."""
		print(f"LOG: {datetime.today()}: {msg}\n")

	def get_base_dir(self):
		"""Get the directory containing code and assets."""
		return self.base_dir

	def get_data_dir(self):
		"""Get the directory containing the data of the application."""
		return self.data_dir

	def get_template_dir(self):
		"""Get the directory containing templates."""
		return self.template_path

	def save_passwords(self):
		"""Save passwords."""
		with open(self.pwd_path, "w") as out:
			for (user, pwd) in self.passwords.items():
				out.write(f"{user}:{pwd}\n" % (user, pwd))

	def load_passwords(self):
		"""Load passwords."""
		self.passwords = {}
		try:
			with open(self.pwd_path) as input:
				num = 0
				for line in input.readlines():
					num += 1
					try:
						i = line.index(':')
					except ValueError:
						self.log(f"bad formatted password line {num}")
					user = line[:i]
					pwd = line[i+1:].strip()
					self.passwords[user] = pwd
		except OSError as e:
			self.log(f"cannot open password: {e}")

	def check_password(self, user, pwd):
		"""Check a password."""
		try:
			return self.passwords[user] == pwd
		except KeyError:
			return False

	def add_password(self, user, pwd):
		"""Add a new password."""
		self.passwords[user] = pwd
		self.save_passwords()

	def new_session(self, man):
		return Session(self, man)

	def load_templates(self):
		"""Load the templates."""
		self.templates = {}
		for name in os.listdir(self.template_path):
			template = Template(self, name)
			template.load()
			self.templates[name] = template

	def get_template(self, name):
		"""Find the template with the given name or return None."""
		try:
			return self.templates[name]
		except KeyError:
			return None

	def get_templates(self):
		"""Get the templates."""
		return self.templates

	def exists_user(self, user):
		"""Test if a user exists."""
		return user in self.passwords

if __name__ == '__main__':

	# parse arguments
	parser = argparse.ArgumentParser(prog="bass", description="BASS server")
	parser.add_argument('--debug', action='store_true', help='enable debugging')
	parser.add_argument('--debug-user', help='automatically log to this user for debugging.')
	parser.add_argument('--debug-project', help='automatically open the project for debugging.')
	args = parser.parse_args()

	# convert argument to configuration
	DEBUG_USER = args.debug_user
	DEBUG_PROJECT = args.debug_project
	DEBUG = args.debug or DEBUG_USER or DEBUG_PROJECT

	# run the server
	assets = os.path.join(os.path.dirname(__file__), "assets")
	orc.run(Application(), dirs=[assets], debug=DEBUG)
