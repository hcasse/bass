#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import os.path
import re

import bass
import bass.arm as config
import orchid as orc
import subprocess


LINE_RE = re.compile("^([^\.]+\.[^:]:[0-9]+:).*$")

class File:

	def __init__(self, name = "main.s"):
		self.name = name

	def get_path(self):
		return os.path.join(self.project.get_path(), self.name)

	def save(self, text):
		path = self.get_path()
		if not os.path.exists(path):
			dir = os.path.dirname(path)
			if not os.path.exists(dir):
				os.makedirs(dir)
		with open(path, "w", encoding="UTF8") as out:
			out.write(text)

	def load(self):
		path = self.get_path()
		if not os.path.exists(path):
			return config.INITIAL_SOURCE
		else:
			with open(path, "r", encoding="UTF8") as inp:
				return inp.read()


class Project:

	def __init__(self, name = "no name"):
		self.name = name
		self.files = []
		self.add_file(File())
		self.exec_path = None

	def add_file(self, file):
		file.project = self
		self.files.append(file)

	def get_path(self):
		return os.path.join(self.user.get_path(), self.name)

	def get_exec_name(self):
		if self.exec_path == None:
			(name, ext) = os.path.splitext(self.files[0].name)
			self.exec_path = "%s.%s" % (name, config.EXEC_EXT)
		return self.exec_path


class User:

	def __init__(self, name = "anonymous"):
		self.name = name
		self.projects = []
		self.add_project(Project())

	def get_path(self):
		return os.path.join(config.DATADIR, self.name)

	def add_project(self, project):
		project.user = self
		self.projects.append(project)



class Session(orc.Session):

	def __init__(self, app, man):
		orc.Session.__init__(self, app, man)
		self.user = User()
		self.project = self.user.projects[0]
		if self.project.files != []:
			self.file = self.project.files[0]
		else:
			self.file = None
		self.sim = None
		self.perform_start = False

	def start_sim(self):
		"""Start the simulation."""
		exec_path = os.path.join(self.project.get_path(), self.project.get_exec_name())
		print("DEBUG: exec_path=", exec_path)
		if not os.path.exists(exec_path):
			self.console.append(orc.text(orc.INFO, "Need to compile."))
			self.perform_start = True
			self.compile()
		else:
			self.perform_start = False
			try:
				self.sim = config.load(exec_path)
				self.enable_sim(True)
				self.console.append(orc.text(orc.INFO, "Start simulation."))
			except bass.Exception as e:
				self.console.append(orc.text(orc.ERROR, "ERROR:") + str(e))

	def stop_sim(self):
		"""Stop the current simulation."""
		self.enable_sim(False)
		self.console.append(orc.text(orc.INFO, "Stop simulation."))
		self.sim.release()
		self.sim = None

	def playstop(self):
		if self.sim != None:
			self.stop_sim()
		else:
			self.start_sim()

	def step(self):
		pass

	def step_over(self):
		pass

	def run_to(self):
		pass

	def go_on(self):
		pass

	def pause(self):
		pass

	def reset(self):
		pass

	def compile(self):
		self.editor.get_content(self.save_and_compile)

	def save_and_compile(self, editor, content):
		self.file.save(content)
		cmd = config.CC_COMMAND % (
				self.project.get_exec_name(),
				self.file.name
			)
		self.console.clear()
		self.console.append("<b>Compiling...</b>")
		self.console.append(cmd)
		rc = subprocess.run(
				cmd,
				shell = True,
				cwd = self.project.get_path(),
				encoding = "UTF8",
				capture_output = True
			)

		for line in rc.stdout.split("\n"):
			self.print_line(line)
		for line in rc.stderr.split("\n"):
			self.print_line(line)
		if rc.returncode != 0:
			self.console.append(orc.text(orc.FAILED, "FAILED..."))
		else:
			self.console.append(orc.text(orc.SUCCESS, "SUCCESS!"))
			if self.perform_start:
				self.start_sim()

	def print_line(self, line):
		m = LINE_RE.match(line)
		if m != None:
			p = m.end(1)
			line = orc.text(orc.INFO, line[:p]) + line[p:]
		self.console.append(line)

	def enable_sim(self, enabled = True):
		self.compile_action.set_enabled(not enabled)
		self.step_action.set_enabled(enabled)
		self.step_over_action.set_enabled(enabled)
		self.run_to_action.set_enabled(enabled)
		self.go_on_action.set_enabled(enabled)
		self.reset_action.set_enabled(enabled)

	def enable_run(self, enabled = True):
		self.enable_sim(not enabled)
		self.set_enabled(enabled)

	def help(self):
		pass

	def about(self):
		pass

	def get_index(self):

		self.user_label = orc.Label(self.user.name)
		self.project_label = orc.Label(self.project.name)

		# prepare run actions
		self.compile_action = orc.Button(orc.Icon("check"),
			on_click=self.compile)
		self.playstop_action = orc.Button(orc.Icon("play", color="green"),
			on_click=self.playstop)
		self.step_action = orc.Button(orc.Icon("braces"),
			on_click=self.step)
		self.step_over_action = orc.Button(orc.Icon("!braces-asterisk"),
			on_click=self.step_over)
		self.run_to_action = orc.Button(orc.Icon("fast-forward"),
			on_click=self.run_to)
		self.go_on_action = orc.Button(orc.Icon("skip-forward"),
			on_click=self.go_on)
		self.pause_action = orc.Button(orc.Icon("pause"),
			on_click=self.pause)
		self.reset_action = orc.Button(orc.Icon("reset"),
			on_click=self.reset)
		self.enable_sim(False)
		self.pause_action.disable()

		# initialize editor
		source = ""
		if self.file != None:
			source = self.file.load()
		self.editor = orc.Editor(init = source)
		self.editor.weight = 4

		# initialize console
		self.console = orc.Console(init = "<b>Welcome to BASS!</b>\n")
		self.console.weight = 1

		# generate the page
		return orc.Page(
			orc.VGroup([
				orc.Header("BASS", [
					orc.Button(image = orc.Icon("box")),
					self.project_label,
					orc.Button(image = orc.Icon("person")),
					self.user_label,
				]),
				orc.ToolBar([
					self.compile_action,
					self.playstop_action,
					self.step_action,
					self.step_over_action,
					self.run_to_action,
					self.go_on_action,
					self.pause_action,
					self.reset_action,
					orc.Spring(hexpand = True),
					orc.Button(orc.Icon("help"),
						on_click=self.help),
					orc.Button(orc.Icon("about"),
						on_click=self.about)
				]),
				orc.VGroup([
					self.editor,
					self.console
				])
			]),
			app = self.get_application()
		)

class Application(orc.Application):

	def __init__(self):
		orc.Application.__init__(self,
			name = "bass",
			authors = ['H. Cassé'],
			license = "GPL v3",
			copyright = "Copyright (c) 2023, University of Toulosue 3",
			description = "Machine level simulator."
		)

	def new_session(self, man):
		return Session(self, man)

if __name__ == '__main__':
	orc.run(Application())
