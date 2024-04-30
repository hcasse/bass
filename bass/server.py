#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import os.path
import re

import bass
import bass.arm as config
import Orchid.orchid as orc
import subprocess
from Orchid.orchid import popup
from Orchid.orchid import dialog
import pandas as pd

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
		
		
	def loadProject(self, path):
		self.files = []
		for f in os.listdir(path):
			if os.path.isfile( os.path.join(path, f) ):
				file = File(name = f)
				self.add_file(file)


class User:

	def __init__(self, name = "anonymous"):
		self.id = 0
		self.name = name
		self.projects = []
		self.add_project(Project())

	def get_path(self):
		return os.path.join(config.DATADIR, str(self.id))

	def add_project(self, project):
		project.user = self
		self.projects.append(project)
	
	
	def loadUser(self, idUser):
		df = pd.read_csv( os.path.join(config.DATADIR,"account.txt") )
		line = df.loc[df['id']==idUser]
		self.id = str(idUser)
		self.name = line.iloc[0, 1]
		self.projects = []

		for p in os.listdir(self.get_path()):
			dirPath = os.path.join(self.get_path(), p)
			if not os.path.isfile(dirPath):
				project = Project(name = p)
				project.loadProject(path = dirPath)
				self.projects.append(project)
		return self
				
	def sigUser(self, name, email, password):
		data = pd.read_csv( os.path.join(config.DATADIR,"account.txt") )
		listID = set(data['id'])
		newID = 1
		while (newID in listID):
			newID += 1
		res = str(newID)+","+name+","+email+","+password+"\n"
		with open(os.path.join(config.DATADIR,"account.txt"), "a", encoding="UTF8") as out:
			out.write(res)
		os.makedirs( os.path.join(config.DATADIR, str(newID)) )
		self.loadUser(newID)


class MyTabEditor(orc.Tab):

	def __init__(self, label, component):
		self.component = component
		self.label = label

	def get_label(self):
		return self.label

	def get_component(self):
		return self.component

	def on_show(self):
		print("Shown", self.label)

	def on_hide(self):
		print("Hidden", self.label)

	def on_release(self):
		print("Released", self.label)

class MyTabConsole(orc.Tab):

	def __init__(self, label, component):
		self.component = component
		self.label = label

	def get_label(self):
		return self.label

	def get_component(self):
		return self.component

	def on_show(self):
		print("Shown", self.label)

	def on_hide(self):
		print("Hidden", self.label)

	def on_release(self):
		print("Released", self.label)


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

	def eventResetButton(self):
		print("Button reset appuye")

	def menuImport(self):
		pass

	def menuSave(self):
		pass

	def menuNew(self):
		pass

	#------------------CAs connecter------------------------
	def connexion(self):
		self.dialogConnexion.show()
	#------------------------end ---------------------------
	
	#-----------creer compte-------------------------
	def eventCreateAccount(self):
		self.dialognewAccount.show()
	#--------------------------------------------------#
	
	#----------------------mot de passe oublie----------#
	def eventforgotPassword(self):
		self.dialogforgotPassword.show()
	#----------------------------------------------------#
 
	def eventCancelButton(self):
		self.dialogConnexion.hide()
		self.dialogforgotPassword.hide()
		self.dialognewAccount.hide()

	def cancelforgotPasswordEvent(self):
		self.dialogforgotPassword.hide()

	def submitEvent(self):
		self.dialogConnexion.hide()
		self.dialognewAccount.hide()
		self.dialogforgotPassword.hide()

	def eventButtonCreateAccount(self):
		self.dialogConnexion.hide()
		self.dialognewAccount.hide()
	#----------------menu button--------------------
	def make_menu(self):
		return popup.MenuButton(
			popup.Menu([
				orc.Button("Importer", on_click=self.menuImport),
				orc.Button("Telecharger", on_click=self.menuSave),
                		orc.Button("Nouveau fichier", on_click=self.menuNew),
			])
		)
	
	#---------------------connexion case------------------------#
	#----------------LayeredPAne connexion-------------------#
	def layeredconnexionDialog(self):
		self.fieldEmail= orc.EmailField(size=20)
		self.fieldMdp= orc.PasswordField(size=20)
		self.username= orc.HGroup([orc.Label("Email"),orc.Spring(hexpand=True),self.fieldEmail, self.connectButton])
		self.mdp= orc.HGroup([orc.Label("Password"), orc.Spring(hexpand=True),self.fieldMdp])

		self.buttonNewAccount= orc.Button("New Account", on_click= self.eventCreateAccount)
		self.lcreercompte= orc.HGroup([orc.Label("Don't have an account"),orc.Spring(hexpand=True), self.buttonNewAccount])
		self.buttonforgotPassword= orc.Button("Retrieve", on_click= self.eventforgotPassword)
		self.lforgotpassword=orc.HGroup([orc.Label("Retrieve"), orc.Spring(hexpand=True),self.buttonforgotPassword])
		self.layeredConnexion= orc.LayeredPane([orc.VGroup([self.username, self.mdp,orc.Spring(vexpand=True), self.lcreercompte ,orc.Spring(vexpand=True), self.lforgotpassword, self.buttonCancel])])
		self.layeredConnexion.weight=10
	
	def layeredCreateAcountDialog(self):
		self.fieldnewUSername= orc.EmailField(size=20)
		self.fieldnewMdp= orc.PasswordField(size=20)
		self.buttonCreate= orc.Button("create", on_click= self.eventButtonCreateAccount)
		self.groupUtilaccount= orc.HGroup([self.buttonCreate, orc.Spring(hexpand=True), self.buttonCancel])
		self.newusername= orc.HGroup([orc.Label("Email"),orc.Spring(hexpand=True),self.fieldEmail])
		self.newmdp= orc.HGroup([orc.Label("Password"), orc.Spring(hexpand=True),self.fieldMdp])
		self.newlayeredConnexion= orc.LayeredPane([orc.VGroup([self.newusername, self.newmdp,orc.Spring(vexpand=True), self.groupUtilaccount])])
		self.newlayeredConnexion.weight=10

	def layeredforgotPassword(self):
		self.fieldRetrieveAccount= orc.EmailField(size=20)
		self.layeredRetrieve= orc.LayeredPane([orc.HGroup([orc.Label("Email"),orc.Spring(hexpand=True),
													 self.fieldRetrieveAccount, orc.Button("Submit", on_click=self.submitEvent),
													 orc.Button("cancel",on_click=self.eventCancelButton)])])


	#---------------------dialog----------------------------#
	def createDialog(self):
		self.make_dialog()
		self.make_dialogNewaccount()
		self.make_dialogforgotPassword()

	def make_dialog(self):
		self.layeredconnexionDialog()
		self.dialogConnexion=dialog.Base(self.page, self.layeredConnexion)
		
	def make_dialogNewaccount(self):
		self.layeredCreateAcountDialog()
		self.dialognewAccount= dialog.Base(self.page, self.newlayeredConnexion)
	
	def make_dialogforgotPassword(self):
		self.layeredforgotPassword()
		self.dialogforgotPassword=dialog.Base(self.page, self.layeredRetrieve)
	
	def connected(self):
		self.dialogConnexion.hide()

	#--------------fonction sur les tab editeur et disassembly---------------
	def add(self):
		self.tabEditeurDisassembly.insert(MyTabEditor("new %d" % self.num, self.editor))
		self.num = self.num + 1
		self.cnt = self.cnt + 1

	def remove(self):
		self.cnt = self.cnt - 1
		self.tabEditeurDisassembly.remove(self.cnt)

	def first(self):
		self.tabEditeurDisassembly.select(self.tabEditeurDisassembly.get_tab(0))

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

		#--------------------initialize editor-------------------
		source = ""
		if self.file != None:
			source = self.file.load()
		self.editor = orc.Editor(init = source)

		# initialize console
		self.console = orc.Console(init = "<b>Welcome to BASS!</b>\n")
		#-------------------initialize register------------------
  
		self.r0= orc.HGroup([orc.Label("R0"), orc.Field(size=10)])
		self.r1= orc.HGroup([orc.Label("R1"), orc.Field(size=10)])
		self.r2= orc.HGroup([orc.Label("R2"), orc.Field(size=10)])
		self.r3= orc.HGroup([orc.Label("R3"), orc.Field(size=10)])
		self.r4= orc.HGroup([orc.Label("R4"), orc.Field(size=10)])
		self.r5= orc.HGroup([orc.Label("R5"), orc.Field(size=10)])
		self.r6= orc.HGroup([orc.Label("R6"), orc.Field(size=10)])
		self.r7= orc.HGroup([orc.Label("R7"), orc.Field(size=10)])
		self.r8= orc.HGroup([orc.Label("R8"), orc.Field(size=10)])
		self.r9= orc.HGroup([orc.Label("R9"), orc.Field(size=10)])
		self.r10= orc.HGroup([orc.Label("R10"), orc.Field(size=10)])
		self.r12= orc.HGroup([orc.Label("R12"), orc.Field(size=10)])
		self.r11= orc.HGroup([orc.Label("R11"), orc.Field(size=10)])
		self.r13= orc.HGroup([orc.Label("R13"), orc.Field(size=10)])
		self.r14= orc.HGroup([orc.Label("R14"), orc.Field(size=10)])
		self.r15= orc.HGroup([orc.Label("R15"), orc.Field(size=10)]) 

		#----------------------------------------------------------#
		
		

		

		#---------------------reset register button------------------------
		self.resetButton= orc.HGroup([orc.Button("Reset",on_click=self.eventResetButton)])

		#------------------register layer---------------------------
		self.registre=orc.LayeredPane([orc.VGroup([self.resetButton,self.r0,self.r1, self.r2, self.r3,
                                           self.r4, self.r5, self.r6, self.r7, self.r8, self.r9,
                                           self.r10, self.r11, self.r12, self.r13, self.r14, self.r15])])
		self.registre.weight=0.10

	
		#-----------editeur + disassembly console -----------
		self.num = 0
		self.cnt = 2

		self.consoleDis=orc.Console(init="Disassembly")

		self.tabEditeurDisassembly = orc.TabbedPane([
			MyTabEditor("main.s", self.editor),
			MyTabConsole("Disassembly", self.consoleDis)
		])

		self.layeredutil= orc.LayeredPane([self.console])
		self.layermemory= orc.LayeredPane([orc.Console(init="espace pour memory")])
		self.layer= orc.LayeredPane([orc.VGroup([self.layeredutil,self.layermemory])])
		
		
		# generate the page
		self.page= orc.Page(
			orc.VGroup([
				orc.Header("BASS", [
					orc.Button(image = orc.Icon("box")),
					self.project_label,
					orc.Button(image = orc.Icon("person"), on_click= self.connexion),
					self.user_label,
				]),
				orc.ToolBar([
					self.make_menu(),
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
				orc.HGroup([
					self.registre,
					orc.VGroup([
					orc.HGroup([
						orc.Button("add", on_click=self.add),
						orc.Button("remove", on_click=self.remove),
						orc.Button("first", on_click=self.first)
					]),
				self.tabEditeurDisassembly]),
				self.layeredutil
				])
			]),
			app = self.get_application()
		)

		#----------------------bouton cancel---------------
		self.connectButton= orc.Button("connect", on_click=self.login)
		self.buttonCancel= orc.Button("cancel", on_click=self.eventCancelButton)
		self.createDialog()
		
		return self.page
		
		
	def login(self):
		email = self.fieldEmail.get_content()
		mdp = self.fieldMdp.get_content()
		if (','in email or ',' in mdp):
			text = "Le caractère spécial , est interdit."
			# La il faut que tu créer un nouveau label en dessous case avec comme texte text
			pass # erreur -> email ou mot de passe incorrecte
		data = pd.read_csv(os.path.join(config.DATADIR,"account.txt"))
		data = data.loc[data['email'] == str(email)]
		if (data.size == 0):
			text = "L'Email n'est pas reconnu"
			# La il faut que tu créer un nouveau label en dessous case avec comme texte text
			pass # erreur -> fonction d'affichage erreur : email non-reconnu
		else:
			mdpCourant = data.iloc[0, 3]
			idUser = data.iloc[0, 0]
			if (mdpCourant == mdp):
				self.user = self.user.loadUser(idUser)
				#
				# C'est la le problème lié à l'actualisation de la page
				self.user_label.set_content(self.user.name)
				self.project_label.set_content(self.user.projects[0].name)
				# La j'ai mit a jour les deux infos en haut, mais il faut que tu change les valeurs pour les fichiers et les projets dans l'affichages
				self.connected()
			else:
				text = "Le mot de passe est erroné"
				# La il faut que tu créer un nouveau label en dessous case avec comme texte text
				pass # erreur -> fonction d'affichage : mot de passe erroné

	def sigin(self, name, email, mdp):
		if (','in email or ',' in mdp or ',' in name):
			text = "Le caractère spécial , est interdit."
			# La il faut que tu créer un nouveau label en dessous case avec comme texte text
			pass # erreur -> email ou mot de passe incorrecte
		data = pd.read_csv(os.path.join(config.DATADIR,"account.txt"))
		listID = set(data['id'])
		if (data.loc[data['email'] == email].size != 0):
			text = "Un compte existe déjà pour cette adresse email."
			# La il faut que tu créer un nouveau label en dessous case avec comme texte text
			pass # erreur -> fonction d'affichage erreur : email déjà
		else:
			self.user = self.user.sigUser(name, email, mdp)
		

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
	orc.run(Application(), debug=True)
