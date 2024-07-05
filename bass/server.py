#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""BASS Application."""

import argparse
import configparser
from datetime import datetime
import os
import os.path
import re
import shutil
import sys

import bass
import bass.arm as config
import Orchid.orchid as orc
import subprocess
from Orchid.orchid import popup
from Orchid.orchid import dialog
import pandas as pd
import bass.utilDisassembly as util

from bass.login import *
from bass.data import *
from bass.registers import RegisterPane
from bass.editors import EditorPane, MyTabConsole

LINE_RE = re.compile(r"^([^\.]+\.[^:]:[0-9]+:).*$")

# debug configuration
DEBUG = False
DEBUG_USER = None
DEBUG_PROJECT = None


class Session(orc.Session):
	def __init__(self, app, man):
		orc.Session.__init__(self, app, man)
		self.user = None
		#self.user.session = self
		self.project = None

		#if self.project.files != []:
		#	self.file = self.project.files[0]
		#else:
		self.file = None
		self.sim = None
		self.perform_start = False
		self.currentProject = None
		self.R = None
		self.Ri = None

		# variables
		self.compiled = orc.Var(False)
		self.started = orc.Var(False)
		self.running = orc.Var(False)

		# compilation and simulation actions
		self.compile_action = orc.Action(self.compile,
			icon=orc.Icon("check"), help="Compile the project.")
		self.playstop_action = orc.Action(self.playstop, enable=self.compiled,
			icon=orc.Icon("play", color="green"), help="Play/stop the simulation.")
		paused = self.started & orc.not_(self.running)
		self.step_action = orc.Action(self.step, enable=paused,
			icon=orc.Icon("braces"), help="Execute one instruction.")
		self.step_over_action = orc.Action(self.step_over, enable=paused,
			icon=orc.Icon("!braces-asterisk"),
			help="Execution one instruction passing over subprogram call.")
		self.run_to_action = orc.Action(self.run_to, enable=paused,
			icon=orc.Icon("fast-forward"), help="Run to current position.")
		self.go_on_action = orc.Action(self.go_on, enable=paused,
			icon=orc.Icon("skip-forward"), help="Go on execution.")
		self.pause_action = orc.Action(self.pause, enable=self.running,
			icon=orc.Icon("pause"), help="Pause the execution")
		self.reset_action = orc.Action(self.reset, enable=paused,
			icon=orc.Icon("reset"), help="Reset the simulation.")

	def get_user(self):
		"""Get the current user."""
		return self.user

	def get_project(self):
		"""Get the current project."""
		return self.project

	def start_sim(self):
		"""Start the simulation."""
		try:
			self.sim = self.get_project().new_sim()
			self.started.set(True)
			self.console.append(orc.text(orc.INFO, "Start simulation."))
		except bass.SimException as e:
			self.console.append(orc.text(orc.ERROR, "ERROR:") + str(e))

	def stop_sim(self):
		"""Stop the current simulation."""
		self.sim.release()
		self.sim = None
		self.started.set(False)
		self.console.append(orc.text(orc.INFO, "Stop simulation."))

	def playstop(self, interface):
		if self.sim is not None:
			self.stop_sim()
		else:
			self.start_sim()

	def step(self, interface):
		#print("Simulateur ",self.sim)
		self.sim.stepInto()
		self.updateFieldRegister()

	def step_over(self, interface):
		while self.sim.nextInstruction()!=self.sim.get_label("_exit"):
			self.step()
		self.step()
		self.stop_sim()

	def run_to(self, interface):
		pass

	def go_on(self, interface):
		pass

	def pause(self, inetrface):
		pass

	def reset(self, interface):
		pass

	def compile(self, n=-1, editor=None, content=None):
		self.editor_pane.save_all(self.then_compile)

	def then_compile(self):
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
			self.console.append(orc.text(orc.SUCCESS, "SUCCESS!"))
			self.compiled.set(True)

	def print_line(self, line):
		m = LINE_RE.match(line)
		if m is not None:
			p = m.end(1)
			line = orc.text(orc.INFO, line[:p]) + line[p:]
		self.console.append(line)

	def enable_sim(self, enabled = True):
		pass
		#self.compile_action.set_enabled(not enabled)
		#self.step_action.set_enabled(enabled)
		#self.step_over_action.set_enabled(enabled)
		#self.run_to_action.set_enabled(enabled)
		#self.go_on_action.set_enabled(enabled)
		#self.reset_action.set_enabled(enabled)

	def enable_run(self, enabled = True):
		pass
		#self.enable_sim(not enabled)
		#self.set_enabled(enabled)

	def print_Disassembly(self):
		"""
			Display of disassembly console.
		"""
		exec_path = os.path.join(self.project.get_path(), self.project.get_exec_name())
		nameFile=os.path.join(self.project.get_path(),"disassembly.txt")
		util.createDiassembly(exec_path, nameFile, self.project.get_path())

		with open(nameFile, 'r') as f:
			lignes = f.readlines()

		for ligne in lignes:
			self.consoleDis.append(ligne)


	def print_Memory(self):
		exec_path = os.path.join(self.project.get_path(), self.project.get_exec_name())
		nameFile=os.path.join(self.project.get_path(),"memory.txt")
		util.createMemory(exec_path,nameFile,self.project.get_path())

		with open(nameFile, 'r') as f:
			lignes = f.readlines()

		for ligne in lignes:
			self.consoleMemory.append(ligne)

	def help(self):
		pass

	def about(self):
		d=dialog.About(self.page)
		d.show()

	def eventResetButton(self):
		self.initRegister()
		print("Button reset appuye")

	def menuImport(self):
		pass

	def menuSave(self):
		pass

	def menuNew(self):
		pass


	#----------------menu button--------------------
	def make_menu(self):
		return popup.MenuButton(
			popup.Menu([
				orc.Button("Importer", on_click=self.menuImport),
				orc.Button("Telecharger", on_click=self.menuSave),
				orc.Button("Nouveau fichier", on_click=self.menuNew)
			])
		)
















	#--------------fonction sur les tab editeur et disassembly---------------
	def addFile(self, file):
		if os.path.exists(os.path.join(
			self.user.projects[self.currentProject].get_path(),
			self.fieldFileName.get_value())
		):
			self.event_error(f"Impossible de nommer le fichier \
				{self.fieldFileName.get_content()}. \
				Ce projet contient déjà un fichier avec ce nom.")
		else:
			file.name = self.fieldFileName.get_value()
			self.user.projects[self.currentProject].add_file(file)
			self.editorTempFile.get_content(file.saveEditeur)
			self.event_hideValidTemplateFile()
			self.event_hideValidNameTemplateFile()
			self.event_hideChoiceFile()

	def addProject(self, project):
		if os.path.exists(os.path.join(self.user.get_path(), self.fieldProjectName.get_value())):
			self.event_error(f"Impossible de nommer le projet \
				{self.fieldProjectName.get_content()}. \
				Un autre de vos projets est déjà nommé comme cela.")
		else:
			oldName = project.name
			tPath = os.path.join(config.DATADIR, str(0))
			dirPath = os.path.join(tPath, oldName)
			project.name = self.fieldProjectName.get_value()
			self.user.add_project(project)
			for f in project.files:
				f.save( f.loadWithPath(os.path.join(dirPath, f.name)) )
			self.loadProjectsGroup()
			#self.loadProjectFilesEditor( len(self.user.projects)-1 )
			self.event_hideChoiceProject()
			self.event_hideValidTemplateProject()
			self.event_hideValidNameTemplateProject()

	def first(self):
		"""first
		"""
		self.tabEditeurDisassembly.select(self.tabEditeurDisassembly.get_tab(0))

	def saveAll(self):
		"""save
		"""
		if self.user.id == -1:
			self.event_errorConnection()
		else:
			self.intCourant = self.tabEditeurDisassembly.current
			self.intPCourant = self.currentProject
			for i in range(len(self.tabEditeurDisassembly.tabs)-1):
				self.tabEditeurDisassembly.select(i+1)
				self.tabEditeurDisassembly.select(i+1)
				file = self.user.projects[self.currentProject].files[i]
				file.AJour = False
				editor = self.tabEditeurDisassembly.tabs[i+1].get_component()
				editor.get_content(file.saveEditeur)

	def renameFile(self):
		"""rename
		"""
		self.tabEditeurDisassembly.tabs[self.currentFint].get_component().get_content(
			lambda: self.currentFile.rename(new_name = self.fieldFileName.get_value()))

	def renameProject(self):
		"""rename
		"""
		#curP = self.currentProject
		verifReturn = self.user.projects[self.currentProject]. \
			rename_project(self.fieldProjectName.get_value())
		if verifReturn != 0:
			self.event_error(verifReturn)
		else:
			self.loadProjectsGroup()
			#self.loadProjectFilesEditor(curP)
			self.tabEditeurDisassembly.select(self.currentFint)
			self.event_hideRenameProject()

	def makeButtonLambdaProject(self, project):
		"""sdf
		"""
		return orc.Button(self.user.projects[project].name)
					#on_click=lambda: self.loadProjectFilesEditor(project))

	def loadProjectFilesEditor(self):
		"""Load the project in the file editor."""

		# update remaining of window
		self.tabEditeurDisassembly.current = -1
		self.tabEditeurDisassembly.panes.current = -1
		self.tabEditeurDisassembly.labs.current = -1
		self.tabEditeurDisassembly.select(self.tabEditeurDisassembly.current)
		self.tabEditeurDisassembly.select(self.tabEditeurDisassembly.current)
		for i in range(len(self.tabEditeurDisassembly.tabs)):
			self.tabEditeurDisassembly.select(i)
			self.tabEditeurDisassembly.select(i)
		if len(self.tabEditeurDisassembly.tabs) > 0 :
			self.first()


	def edit_user(self):
		"""Start editing user."""
		pass

	def get_index(self):

		self.user_label = orc.Label("")
		self.user_label.set_style("min-width", "8em")
		self.project_label = orc.Label("")
		self.project_label.set_style("min-width", "8em")

		# prepare run actions
		#self.playstop_action = orc.Button(orc.Icon("play", color="green"),
		#	on_click=self.playstop)

		# initialize console
		self.console = orc.Console(init = "<b>Welcome to BASS!</b>\n")

		self.consoleDis=orc.Console(init="Disassembly")

		#--------------------------Panel de gauche-----------------------------#
		self.consoleMemory= orc.Console(init="")
		hlist = []
		hIntern = []
		hIntern.append(orc.Spring(hexpand=True))
		if self.user is not None:
			for i in range(len(self.user.projects)):
				if (i%3 == 0 and i!=0):
					hlist.append( orc.HGroup(hIntern) )
					hIntern = []
					hIntern.append(orc.Spring(hexpand=True))
				but = self.makeButtonLambdaProject(i)
				hIntern.append(but)
				hIntern.append(orc.Spring(hexpand=True))
		hlist.append( orc.HGroup(hIntern) )
		l = [
			orc.Spring(vexpand=True),
			orc.Spring(vexpand=True),
			orc.HGroup([
					orc.Label("Liste de vos Projets :"),
					orc.Spring(hexpand=True),
				#orc.Button("Ajouter un nouveau projet",
				#	on_click=self.event_templateProject)
				]),
				orc.Spring(vexpand=True)
		]
		l.extend(hlist)


		self.projectsGroup = orc.VGroup(l)


		self.tabMemoryProjet = orc.TabbedPane([
			MyTabConsole("Memory",self.consoleMemory),
			MyTabConsole("Projets",self.projectsGroup)
		])
		self.memoryConsoleGroup = self.tabMemoryProjet

		# generate the page
		self.register_pane = RegisterPane()
		self.editor_pane = EditorPane()
		editor_group = HGroup([
			self.editor_pane,
			self.memoryConsoleGroup
		])
		editor_group.weight = 3
		self.console.weight = 1
		self.page = orc.Page(
			orc.VGroup([
				orc.Header("BASS", [
					orc.Button(image = orc.Icon("box")),
					self.project_label,
					orc.Button(image = orc.Icon("person"), 			on_click=self.edit_user),
					self.user_label,
				]),
				orc.ToolBar([
					self.make_menu(),
					orc.Button(self.compile_action),
					orc.Button(self.playstop_action),
					orc.Button(self.step_action),
					orc.Button(self.step_over_action),
					orc.Button(self.run_to_action),
					orc.Button(self.go_on_action),
					orc.Button(self.pause_action),
					orc.Button(self.reset_action),
					orc.Spring(hexpand = True),
					orc.Button(orc.Icon("help"), on_click=self.help),
					orc.Button(orc.Icon("about"), on_click=self.about)
				]),
				orc.HGroup([
					self.register_pane,
					VGroup([
						editor_group,
						self.console
					])
				])
			]),
			app = self.get_application()
		)

		# reset UI
		self.register_pane.init()

		# prepare dialogs
		self.login_dialog = LoginDialog(self, self.page)
		self.register_dialog = None
		self.select_dialog = None

		# perform connection
		if DEBUG:
			self.get_application().log("entering debugging mode!")

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


	# Connecting functions

	def setup_project(self, project):
		"""Setup the project in the main window."""

		# display project
		self.project = project
		self.project_label.set_text(project.get_name())

		# setup editors
		self.editor_pane.clear()
		for file in self.project.get_sources():
			self.editor_pane.open_source(file)

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
		print("LOG: %s: %s\n" % (datetime.today(), msg))

	def get_base_dir(self):
		"""Get the directory containing code and assets."""
		return self.root_dir

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
				out.write("%s:%s\n" % (user, pwd))

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
						self.log("bad formatted password line %s" % num)
					user = line[:i]
					pwd = line[i+1:].strip()
					self.passwords[user] = pwd
		except OSError as e:
			self.log("cannot open password: %s" % e)

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
	print("DEBUG: assets =", assets)
	orc.run(Application(), debug=DEBUG, dirs=[assets])
