
"""Module containing the classes of the user/project database."""

import configparser
import os
import os.path
import re
import shutil
import subprocess

import bass
from bass import arm

class DataException(Exception):
	"""Error raised by the database."""

	def __init__(self, msg):
		Exception.__init__(self)
		self.msg = msg

	def __str__(self):
		return self.msg


def error(app, msg):
	"""Raise an error and log the error."""
	app.log(msg)
	raise DataException(msg)


class Disassembly(bass.Disassembly):
	"""Disassembly for objdump output."""

	LABEL_RE = re.compile(r"^([0-9a-fA-F]+)\s+<([^>]+)+>:")
	INST_RE = re.compile(r"^\s*([0-9a-fA-F]+):\s+([0-9a-fA-F]+)\s+(.*)")

	def __init__(self, output):
		bass.Disassembly.__init__(self)
		self.lines = []
		self.labels = {}
		base = ""
		for line in output.split('\n'):

			# look for a label
			match = self.LABEL_RE.match(line)
			if match is not None:
				base = match.group(1)
				addr = int(base, 16)
				label = match.group(2)
				self.labels[label] = addr
				self.lines.append((addr, "", f"{label}:"))
				continue

			# look for an instruction
			match = self.INST_RE.match(line)
			if match is not None:
				addr = match.group(1)
				if len(addr) < len(base):
					addr = base[0:len(base)-len(addr)] + addr
				self.lines.append((int(addr, 16), match.group(2), match.group(3)))
				continue

	def get_code(self):
		return self.lines

	def find_label(self, label):
		try:
			return self.labels[label]
		except KeyError:
			return None


class File:

	def __init__(self, name = "main.s"):
		self.name = name
		self.project = None
		self.currentFint = None

	def get_name(self):
		"""Get the name of the file."""
		return self.name

	def get_path(self):
		"""Ge the path of the file."""
		return os.path.join(self.project.get_path(), self.name)

	def save(self, text):
		"""Save the file to the disk."""
		path = self.get_path()
		with open(path, "w", encoding="UTF8") as out:
			out.write(text)

	def load(self):
		"""Load the file from the disk."""
		path = self.get_path()
		with open(path, "r", encoding="UTF8") as inp:
			return inp.read()

	def delete(self):
		"""Delete a file."""
		path = self.get_path()
		os.remove(path)

	def rename(self, new_name, editeur, text):
		"""
			Fonction permettant de renommer un fichier.

			  @param new_name : Le nouveau nom du fichier.
			  @param text : Le contenu à sauvegarder dans le fichier renommé.
		"""
		if not os.path.exists(self.get_path):
			self.project.user.session.event_error("Le fichier "+self.name+" n'a pas été trouvé.")
		elif os.path.exists(os.path.join(self.project.get_path(), new_name)):
			self.project.user.session.event_error(
				f"Impossible de nommer le fichier {new_name}. \
				Ce projet contient déjà un fichier avec ce nom.")
		else:
			self.delete()
			self.name = new_name
			self.save(text)
			session = self.project.user.session
			session.loadProjectFilesEditor()
			session.tabEditeurDisassembly.select(self.currentFint)
			session.event_hideRenameFile()


class Template:
	"""Represents a template."""

	def __init__(self, app, name):
		"""Build a template with given name."""
		self.app = app
		self.name = name
		self.description = ""
		self.hide = []
		self.exec = "main.elf"
		self.sources = ["main.s"]
		self.arch = "arm"
		self.path = os.path.join(app.get_template_dir(), self.name)
		self.install = []

	def get_name(self):
		"""Get the name of the template."""
		return self.name

	def is_hidden(self, file):
		"""Check if the given file is hidden, not show to the user, in the current template."""
		return file in self.hide

	def load(self):
		"""Load the template from its description file."""
		path = os.path.join(self.path, "template.ini")
		config = configparser.ConfigParser()
		config.read(path)
		self.description = config.get("template", "description", fallback="")
		self.hide = config.get("template", "hide", fallback="").split(";")
		self.exec = config.get("template", "exec", fallback="main.elf")
		self.sources = config.get("template", "sources", fallback="main.s").split(";")
		self.install = config.get("template", "install", fallback="main.s").split(";")
		self.arch = config.get("template", "arch", fallback="arm")

	def instantiate(self, to):
		"""Install the template in the to directory. May raise DataException."""
		try:
			for file in self.install:
				shutil.copy(os.path.join(self.path, file), to)
		except OSError as e:
			error(self.app, f"template file {file} cannot be copied to {to}: {e}")

	def __str__(self):
		return self.name

	def get_exec_name(self):
		"""Get the executable name."""
		return self.exec


class Project:
	"""The project of a user."""

	def __init__(self, user, name, template=None):
		self.app = user.app
		self.user = user
		self.name = name
		self.files = None
		self.template = template
		self.path = None
		self.disasm = None

	def get_name(self):
		"""Get the name of the project."""
		return self.name

	def get_path(self):
		"""Get the path to the directory of the project."""
		if self.path is None:
			self.path = os.path.join(self.user.get_path(), self.name)
		return self.path

	def get_ini_path(self):
		"""Get the path of .ini file of the project."""
		return os.path.join(self.get_path(), "project.ini")

	def get_exec_path(self):
		"""Get the path of the executable."""
		return os.path.join(self.get_path(), self.template.get_exec_name())

	def get_sources(self):
		"""Return source files of the project."""
		for file in self.get_files():
			if not self.template.is_hidden(file.get_name()) \
			and file.get_name().endswith(".s"):
				yield file

	def add_file(self, file):
		"""Add a file to a project."""
		if self.files is None:
			self.load()
		file.project = self
		self.files.append(file)

	def get_files(self):
		"""Get the files of the project."""
		if self.files is None:
			self.files = []
			for name in os.listdir(self.get_path()):
				if not self.template.is_hidden(name) and \
				os.path.isfile(os.path.join(self.get_path(), name)):
					file = File(name)
					self.add_file(file)
		return self.files

	def load(self):
		"""Load the content of a project."""
		config = configparser.ConfigParser()
		config.read(self.get_ini_path())
		tname = config.get("project", "template", fallback="")
		self.template = self.app.get_template(tname)
		if self.template is None:
			self.app.log(f"no template named {tname}")
			self.template = Template(self.app, tname)

	def delete_project(self):
		"""Remove a project."""
		path = self.get_path()
		if os.path.exists(path):
			shutil.rmtree(path)
			return True
		return False

	def rename_project(self, new_name):
		"""Rename a project."""
		os.rename(self.get_path(), os.path.join(self.user.get_path(), new_name))
		self.name = new_name

	def create(self):
		"""Create from a file name."""

		# create directory
		path = self.get_path()
		try:
			os.mkdir(path)
		except OSError as e:
			error(self.app, f"cannot create project directory {path}: {e}")

		# copy files
		try:
			self.template.instantiate(path)
		except DataException as e:
			shutil.rmtree(path)
			error(self.app, str(e))

		# save configuration
		config = configparser.ConfigParser()
		config['project'] = {}
		config['project']['template'] = self.template.get_name()
		try:
			with open(self.get_ini_path(), "w") as out:
				config.write(out)
		except OSError as e:
			shutil.rmtree(path)
			error(self.app, f"cannot write project config into project {self.name}: {e}")

	def __str__(self):
		return self.name

	def compile(self):
		"""Compile the project. Return a triple (command result, output text, error text)."""
		self.disasm = None
		cp = subprocess.run(
				"make",
				shell = True,
				cwd = self.get_path(),
				encoding = "UTF8",
				capture_output = True
			)
		return (cp.returncode, "make\n" + cp.stdout, cp.stderr)

	def new_sim(self):
		"""Start simulator for the project executable.
		Return the simulator. If there is an error, raises a SimException."""
		return arm.Simulator(self.get_exec_path())

	def get_disasm(self):
		"""Get the disassembly of the current program."""

		if self.disasm is None:

			# get information
			cp = subprocess.run(
					"make disasm",
					shell = True,
					cwd = self.get_path(),
					encoding = "UTF8",
					capture_output = True
				)

			# build the disassembly
			if cp.returncode == 0:
				self.disasm = Disassembly(cp.stdout)
			else:
				raise bass.DisassemblyException(cp.stderr.replace('\n', ' '))

		return self.disasm

	def get_arch(self):
		"""Get the architecture used in this project."""
		return arm.Simulator.get_arch()


class User:
	"""A user."""

	def __init__(self, app, name, email=""):
		self.app = app
		self.name = name
		self.email = email
		self.projects = []
		self.path = None

	def get_name(self):
		return self.name

	def get_path(self):
		"""Get the directory of the user."""
		if self.path is None:
			self.path = os.path.join(self.app.get_data_dir(), self.name)
		return self.path

	def get_account_path(self):
		""""Get the path of the account .ini file."""
		return os.path.join(self.get_path(), "account.ini")

	def add_project(self, project):
		""""Add a project to the user."""
		project.user = self
		self.projects.append(project)

	def remove_project(self, project):
		"""Remove a project from the user."""
		if project in self.projects:
			self.projects.remove(project)
			project.delete_project()

	def get_projects(self):
		return self.projects

	def load(self):
		"""Load data from the user."""
		config = configparser.ConfigParser()
		config.read(self.get_account_path())
		self.email = config.get("user", "email", fallback="")
		for name in config.get("user", "projects").split(";"):
			if name != "":
				self.add_project(Project(self, name))

	def save(self):
		"""Save the user file."""
		config = configparser.ConfigParser()
		config['user'] = {}
		config['user']['email'] = self.email
		config['user']['projects'] = ";".join([p.name for p in self.projects])
		with open(self.get_account_path(), "w") as out:
			config.write(out)

	def create(self):
		"""Create the user: its directory and .ini file."""
		try:
			os.mkdir(self.get_path())
		except OSError as e:
			error(self.app, f"cannot create directory for user {self.name}: {e}")
		try:
			self.save()
		except DataException as e:
			shutil.rmtree(self.path)
			error(self.app, str(e))
