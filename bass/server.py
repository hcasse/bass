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
		"""
			Fonction permattant d'initialiser un objet Project

			  @param name : Le nom du projet a initialiser (par defaut "no name").
		"""
		self.name = name
		self.files = []
		self.add_file(File())
		self.exec_path = None

	def add_file(self, file):
		"""
			Fonction permettant d'ajouter un objet File a un objet Project.

			  @param file : L'objet File a ajouter a l'objet Project.
		"""
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
		"""
			Fonction permettant d'actualiser un objet Project a partir de l'adresse du repertoire systeme.

			  @param path : L'adresse du repertoire systeme ou est stocke le projet et ses fichiers.
		"""
		self.files = []
		for f in os.listdir(path):
			if os.path.isfile( os.path.join(path, f) ):
				file = File(name = f)
				self.add_file(file)


class User:

	def __init__(self, name = "anonymous"):
		"""
			Fonction permettant d'initialiser un objet User.

			  @param name : Le nom de l'utilisateur (par defaut "anonymous").
		"""
		self.id = 0
		self.name = name
		self.projects = []
		self.add_project(Project())

	def get_path(self):
		"""
			Fonction permettant d'obtenir l'adresse du repertoir systeme de l'utilisateur.
		"""
		return os.path.join(config.DATADIR, str(self.id))

	def add_project(self, project):
		"""
			Fonction permettant d'ajouter un objet Projet a un objet User

			  @param project : Le projet a ajouter a l'objet User.
		"""
		project.user = self
		self.projects.append(project)
	
	
	def loadUser(self, idUser):
		"""
			Fonction permettant de se connecter a un compte utilisateur.

			  @param idUser : L'identifiant systeme de l'utilisateur.

			  @return L'objet User mit a jour avec les informations du compte utilisateur rattache a l'identifiant systeme idUser.
		"""
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
				project.user = self
				self.projects.append(project)
		return self
				
	def sigUser(self, name, email, password):
		"""
			Fonction permettant de creer un compte utilisateur a partir des informations necessaires.

			  @param name : Le nom, ou pseudo, de l'utilisateur.
			  @param email : L'email de l'utilisateur.
			  @param password : Le mot de passe de l'utilisateur.

			  @return Le resultat de la fonction loadUser avec comme parametre le nouvel id de l'utilisateur.
		"""
		data = pd.read_csv( os.path.join(config.DATADIR,"account.txt") )
		listID = set(data['id'])
		newID = 1
		while (newID in listID):
			newID += 1
		res = str(newID)+","+name+","+email+","+password+"\n"
		with open(os.path.join(config.DATADIR,"account.txt"), "a", encoding="UTF8") as out:
			out.write(res)
		os.makedirs( os.path.join(config.DATADIR, str(newID)) )
		return self.loadUser(newID)

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
				self.consoleDis.clear()
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
		#print("Simulateur ",self.sim)
		retour=self.sim.stepInto()
		self.consoleDis.append(retour)
		self.updateFieldRegister()

	def step_over(self):
		while self.sim.nextInstruction()!=self.sim.get_label("_exit"):
			self.step()
		self.step()
		self.stop_sim()

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


	def eventError(self, texte):
		"""
			Fonction permettant de creer une fenetre de dialogue d'erreurs. 

			  @param texte : Le texte d'erreur a afficher dans la fenetre de dialogue d'erreurs.
		"""
		self.make_dialogError(texte)
		self.dialogError.show()

	def eventRenameFile(self):
		"""
		"""
		pass

	def eventRenameProject(self):
		"""
		"""
		pass

	#----------------------------------------------------#
	def eventCancelError(self):
		"""
			Fonction permettant de faire disparaitre la fenetre de dialogue d'erreurs.
		"""
		self.dialogError.hide()

	def cancelRenameFile(self):
		self.dialogRenameFile.hide()

	def cancelRenameProject(self):
		self.dialogRenameProject.hide()

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

	def eventDisconnect(self):
		self.dialogDeconnexion.hide()

	#----------------menu button--------------------
	def make_menu(self):
		return popup.MenuButton(
			popup.Menu([
				orc.Button("Importer", on_click=self.menuImport),
				orc.Button("Telecharger", on_click=self.menuSave),
                orc.Button("Nouveau fichier", on_click=self.menuNew)
			])
		)
	
	#---------------------connexion case------------------------#
	#----------------LayeredPAne connexion-------------------#
	def layeredconnexionDialog(self):
		self.fieldEmail= orc.EmailField(label="Email", size=20)
		self.fieldMdp= orc.PasswordField(label="Password",size=20)
		self.username= orc.HGroup([self.fieldEmail, self.connectButton])
		self.mdp= orc.HGroup([self.fieldMdp])

		self.buttonNewAccount= orc.Button("New Account", on_click= self.eventCreateAccount)
		self.lcreercompte= orc.HGroup([orc.Label("Don't have an account"),orc.Spring(hexpand=True), self.buttonNewAccount])
		self.buttonforgotPassword= orc.Button("Retrieve", on_click= self.eventforgotPassword)
		self.lforgotpassword=orc.HGroup([orc.Label("Retrieve"), orc.Spring(hexpand=True),self.buttonforgotPassword])
		self.layeredConnexion= orc.LayeredPane([orc.VGroup([self.username, self.mdp,orc.Spring(vexpand=True), self.lcreercompte ,orc.Spring(vexpand=True), self.lforgotpassword, self.buttonCancel])])
		self.layeredConnexion.weight=10

	def layeredDeconnexionDialog(self):
		self.layeredDeconnexion= orc.LayeredPane([orc.Button("Disconnect", on_click= self.eventDisconnect)])
		self.layeredDeconnexion.weight=10

	def layeredCreateAcountDialog(self):
		self.fieldNom= orc.Field(size=20)
		self.fieldnewUSername= orc.EmailField(label="Email",size=20)
		self.fieldnewMdp= orc.PasswordField(label="Password",size=20)
		self.buttonCreate= orc.Button("create", on_click= self.eventButtonCreateAccount)
		self.groupUtilaccount= orc.HGroup([self.buttonCreate, orc.Spring(hexpand=True), self.buttonCancel])
		self.newNom= orc.HGroup([orc.Label("Username"), orc.Spring(hexpand=True),self.fieldNom])
		self.newlayeredConnexion= orc.LayeredPane([orc.VGroup([self.fieldnewUSername, self.newNom,self.fieldnewMdp,orc.Spring(vexpand=True), self.groupUtilaccount])])
		self.newlayeredConnexion.weight=10

	def layeredforgotPassword(self):
		self.fieldRetrieveAccount= orc.EmailField(label="Email",size=20)
		self.layeredRetrieve= orc.LayeredPane([orc.HGroup([self.fieldRetrieveAccount, orc.Button("Submit", on_click=self.submitEvent),
													 orc.Button("cancel",on_click=self.eventCancelButton)])])

	def layeredErroR(self, texte):
		"""
			Fonction permettant de creer le contenue d'une fenetre de dialogue servant a la gestion des messages d'erreurs.

			  @param texte : Le message d'erreur qui sera contenu par la fenetre de dialogue.
		"""
		self.msgError = orc.HGroup([orc.Label(texte)])
		self.layeredError = orc.LayeredPane([orc.VGroup([self.msgError, orc.Spring(hexpand=True), orc.Button("Ok", on_click=self.eventCancelError)])])
		self.layeredError.weight = 10

	def layeredRenameFichier(self, filename = ""):
		"""
		"""
		self.fieldFileName = orc.Field(size=20, init=filename)
		self.layeredRenameFile = orc.LayeredPane([ orc.VGroup([ orc.HGroup([orc.Label("Entrez le nouveau nom du fichier : ")]), orc.HGroup([orc.Spring(hexpand=True), self.fieldFileName]), orc.Spring(vexpand=True),
																orc.HGroup([orc.Button("Annuler", on_click = self.cancelRenameFile), orc.Spring(hexpand=True), orc.Button("Valider", on_click= self.renameFichier)]) ])])
		self.layeredRenameFile.weight = 10

	def layeredRenameProject(self, projectname = ""):
		"""
		"""
		self.fieldProjectName = orc.Field(size=20, init=projectname)
		self.layeredRenameProjet = orc.LayeredPane([ orc.VGroup([ orc.HGroup([orc.Label("Entrez le nouveau nom du projet : ")]), self.fieldProjectName, orc.Spring(vexpand=True),
																orc.HGroup([orc.Button("Annuler", on_click = self.cancelRenameFile), orc.Spring(hexpand=True), orc.Button("Valider", on_click= self.renameProjet)]) ])])
		self.layeredRenameProjet.weight = 10


	def updateFieldRegister(self):
		"""
			Update the register of the interface.
		"""
		self.R = None
		self.Ri = None
		registerBanks=self.sim.getNbRegisterBank()
		print("NB banque de registre = ",registerBanks)
		for i in range(0, registerBanks):
			bank = self.sim.getRegisterBank(i)
			if bank[0] == 'R':
				self.R = bank
				self.Ri = i
			if bank[2] == 1:
				self.fieldRegistre[16].set_value(hex(self.sim.getRegister(i, 0)))
			for j in range(0, bank[2]):
					self.fieldRegistre[j].set_value(hex(self.sim.getRegister(i, j)))
		
	def updateRegisterFromField(self):
		"""
			Update register value from field.
		"""
		Ritemp= self.sim.getRegisterBanks()
		for i in range(13):
			self.sim.setRegister(Ritemp,i,self.fieldRegistre[0].get_content())
		


	def initRegister(self):
		"""
			Initialize the register to 0.
		"""
		for i in range(13):
			self.fieldRegistre[i].set_value(hex(0))
		

	#---------------------dialog----------------------------#
	def createDialog(self):
		"""
			Create all useful dialogs for initialization.
		"""

		self.make_dialog()
		self.make_dialogError()
		self.make_dialogNewaccount()
		self.make_dialogforgotPassword()
		self.make_dialogRenameProjet()
		self.make_dialogRenameFichier()
		self.make_dialogDeconnexion()


	def make_dialogError(self, texte=""):
		"""
			Fonction permettant de creer une fenetre de dialogue pour la gestion des messages erreurs.

			  @param texte : Le message d'erreur qui sera contenu par la fenetre de dialogue.
		"""
		self.layeredErroR(texte)
		self.dialogError = dialog.Base(self.page, self.layeredError)

	def make_dialogRenameFichier(self, texte=""):
		"""
		"""
		self.layeredRenameFichier(texte)
		self.dialogRenameFile = dialog.Base(self.page, self.layeredRenameFile)

	def make_dialogRenameProjet(self, texte=""):
		"""
		"""
		self.layeredRenameProject(texte)
		self.dialogRenameProject = dialog.Base(self.page, self.layeredRenameProjet)

	def make_dialog(self):
		"""
			Event handler to create the dialog (connection).
		"""
		self.layeredconnexionDialog()
		self.dialogConnexion=dialog.Base(self.page, self.layeredConnexion)
		
	def make_dialogNewaccount(self):
		"""
			Event handler to create the dialog (new account).
		"""
		self.layeredCreateAcountDialog()
		self.dialognewAccount= dialog.Base(self.page, self.newlayeredConnexion)
	
	def make_dialogforgotPassword(self):
		"""
			Event handler to create the dialog (forgotPassword).
		"""
		self.layeredforgotPassword()
		self.dialogforgotPassword=dialog.Base(self.page, self.layeredRetrieve)

	def make_dialogDeconnexion(self):
		"""
			Event handler to create the dialog (deconnexion).
		"""
		self.layeredDeconnexionDialog()
		self.dialogDeconnexion= dialog.Base(self.page,self.layeredDeconnexion)
	
	def connected(self):
		"""
			Event handler to close the dialog (connetion).
		"""
		self.dialogConnexion.hide()

	#--------------fonction sur les tab editeur et disassembly---------------
	def add(self):
		"""
		"""
		self.tabEditeurDisassembly.insert(MyTabEditor("new %d" % self.num, self.editor))
		self.num = self.num + 1
		self.cnt = self.cnt + 1

	def remove(self):
		"""
		"""
		self.cnt = self.cnt - 1
		self.tabEditeurDisassembly.remove( self.tabEditeurDisassembly.current )
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

	def first(self):
		"""
		"""
		self.tabEditeurDisassembly.select(self.tabEditeurDisassembly.get_tab(0))

	def renameFile(self):
		"""
		"""
		self.currentFint = self.tabEditeurDisassembly.current
		self.currentFile = self.user.projects[self.currentProject][self.currentFint-1]
		pass

	def renameFichier(self):
		pass
		
	def renameProjet(self):
		pass

	def loadProjectsGroup(self):
		"""
		"""
		for i in range(len(self.projectsGroup.get_children())-2):
			self.projectsGroup.remove(len(self.projectsGroup.get_children())-(i+1))
		for i in range(len(self.user.projects)):
			but = self.makeButtonLambdaProject(self.user.projects[i])
			self.projectsGroup.insert(orc.HGroup([but]))

	def makeButtonLambdaProject(self, project):
		"""
		"""
		return orc.Button(project.name, on_click=lambda: self.loadProjectFilesEditor(project))
		

	def loadProjectFilesEditor(self, projet):
		"""
		"""
		self.currentProject = projet
		self.project_label.set_content(projet.name)
		for _ in range(len(self.tabEditeurDisassembly.tabs)-1):
			self.tabEditeurDisassembly.remove(1)
		for f in projet.files:
			if ( (".s" in f.name) and not(".elf" in f.name) ):
				t = MyTabEditor(f.name, orc.Editor(init = f.load()))
				self.tabEditeurDisassembly.insert(t)
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

		#------------------create field--------------------------
		self.fieldRegistre=[orc.Field(size=10) for _ in range(13)]
		
		#--------------create read-only register-----------------
		for i in range(4):
			self.fieldRegistre.append(orc.Field(size=10,read_only=True))
		
		self.fieldR0= orc.Field(size=10)
		
		#-------------------initialize register------------------
		self.r0= orc.HGroup([orc.Label("R0"), self.fieldRegistre[0]])
		self.r1= orc.HGroup([orc.Label("R1"), self.fieldRegistre[1]])
		self.r2= orc.HGroup([orc.Label("R2"), self.fieldRegistre[2]])
		self.r3= orc.HGroup([orc.Label("R3"), self.fieldRegistre[3]])
		self.r4= orc.HGroup([orc.Label("R4"), self.fieldRegistre[4]])
		self.r5= orc.HGroup([orc.Label("R5"), self.fieldRegistre[5]])
		self.r6= orc.HGroup([orc.Label("R6"), self.fieldRegistre[6]])
		self.r7= orc.HGroup([orc.Label("R7"), self.fieldRegistre[7]])
		self.r8= orc.HGroup([orc.Label("R8"), self.fieldRegistre[8]])
		self.r9= orc.HGroup([orc.Label("R9"), self.fieldRegistre[9]])
		self.r10= orc.HGroup([orc.Label("R10"), self.fieldRegistre[10]])
		self.r11= orc.HGroup([orc.Label("R11"), self.fieldRegistre[11]])
		self.r12= orc.HGroup([orc.Label("R12"), self.fieldRegistre[12]])
		self.r13= orc.HGroup([orc.Label("sp"), self.fieldRegistre[13]])
		self.r14= orc.HGroup([orc.Label("lr"), self.fieldRegistre[14]])
		self.r15= orc.HGroup([orc.Label("pc"), self.fieldRegistre[15]])
		self.cpsr= orc.HGroup([orc.Label("CPSR"), self.fieldRegistre[16]]) 

		#--------------liste des registres---------------------
		self.listregister=[self.r0,self.r1, self.r2,self.r3,self.r4,self.r5, self.r6
					 ,self.r7,self.r8,self.r9,self.r10,self.r11,self.r12,self.r13,self.r14,self.r15,self.cpsr]
		#----------------------------------------------------------#
		#----------------------------------------------------------#
		

		

		#---------------------reset register button------------------------
		self.resetButton= orc.HGroup([orc.Button("Reset",on_click=self.eventResetButton)])

		#------------------register layer---------------------------
		self.registre=orc.LayeredPane([orc.VGroup([self.resetButton,self.r0,self.r1, self.r2, self.r3,
                                           self.r4, self.r5, self.r6, self.r7, self.r8, self.r9,
                                           self.r10, self.r11, self.r12, self.r13, self.r14, self.r15,self.cpsr])])
		self.registre.weight=0.10

	
		#-----------editeur + disassembly console -----------
		self.num = 0
		self.cnt = 2

		self.consoleDis=orc.Console(init="Disassembly")

		self.tabEditeurDisassembly = orc.TabbedPane([
			MyTabConsole("Disassembly", self.consoleDis),
			MyTabEditor("main.s", self.editor)
		])


		#--------------------------Panel de gauche-----------------------------#
		self.consoleMemory= orc.Console(init="")
		hlist = []
		for i in range(len(self.user.projects)):
			but = self.makeButtonLambdaProject(self.user.projects[i])
			hlist.append(orc.HGroup([but]))
		l = [orc.HGroup([orc.Label("Liste de vos Projets :")]), orc.Spring(vexpand=True)]
		l.extend(hlist)
		self.projectsGroup = orc.VGroup(l)
		#self.layeredProjet= orc.LayeredPane([orc.Label("Panel qui contiendra les templates a vous de metrre les templates a l'interieur (et aussi ce qui se passe quand on choisit un template) le panel se trouve a la ligne 482")])
		self.tabMemoryProjet=orc.TabbedPane([MyTabConsole("Memory",self.consoleMemory), MyTabConsole("Projets",self.projectsGroup)])
		self.memoryConsoleGroup=orc.VGroup([self.tabMemoryProjet,self.console])
		
		
		# generate the page
		self.page= orc.Page(
			orc.VGroup([
				orc.Header("BASS", [
					orc.Button(image = orc.Icon("box")),
					self.project_label,
					orc.Button(image = orc.Icon("person"), on_click=self.connexion),
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
				self.memoryConsoleGroup
				])
			]),
			app = self.get_application()
		)

		#----------------------bouton cancel---------------
		self.connectButton= orc.Button("connect", on_click=self.login)
		self.buttonCancel= orc.Button("cancel", on_click=self.eventCancelButton)
		self.createDialog()
		self.initRegister()
		return self.page
		
		
	def login(self):
		"""
			La fonction qui recupere dans la fenetre de dialogue les informations entrees par l'utilisateur, et permet de se connecter, tout en gerant les exceptions.
		"""
		email = self.fieldEmail.get_content()
		mdp = self.fieldMdp.get_content()
		if (',' in email or ',' in mdp):
			text = "Le caractere special , est interdit."
			self.eventError(text)
		else:
			data = pd.read_csv(os.path.join(config.DATADIR,"account.txt"))
			data = data.loc[data['email'] == str(email)]
			if (data.size == 0):
				text = "L'Email n'est pas reconnu"
				self.eventError(text)
			else:
				mdpCourant = data.iloc[0, 3]
				idUser = data.iloc[0, 0]
				if (mdpCourant == mdp):
					self.user = self.user.loadUser(idUser)
					self.user_label.set_content(self.user.name)
					if len(self.user.projects) == 0:
						pass
					else :
						self.loadProjectsGroup()
						self.loadProjectFilesEditor(self.user.projects[0])
						"""
						self.project_label.set_content(self.user.projects[0].name)
						for _ in range(len(self.tabEditeurDisassembly.tabs)-1):
							self.tabEditeurDisassembly.remove(1)
						for f in self.user.projects[0].files:
							if ( (".s" in f.name) and not(".elf" in f.name) ):
								t = MyTabEditor(f.name, orc.Editor(init = f.load()))
								self.tabEditeurDisassembly.insert(t)
						"""
					self.connected()
				else:
					text = "Le mot de passe est errone"
					self.eventError(text)

	def sigin(self):
		"""
			La fonction qui recupere dans la fenetre de dialogue les informations entrees par l'utilisateur, et permet de creer un compte, tout en gerant les exceptions.
		"""
		name = self.fieldNom.get_content()
		email = self.fieldEmail.get_content()
		mdp = self.fieldMdp.get_content()
		if (','in email or ',' in mdp or ',' in name):
			text = "Le caractere special , est interdit."
			self.eventError(text)
		data = pd.read_csv(os.path.join(config.DATADIR,"account.txt"))
		listID = set(data['id'])
		if (data.loc[data['email'] == email].size != 0):
			text = "Un compte existe deja pour cette adresse email."
			self.eventError(text)
		else:
			self.user.sigUser(name, email, mdp)
			self.login()
			self.eventButtonCreateAccount()
		

class Application(orc.Application):

	def __init__(self):
		orc.Application.__init__(self,
			name = "bass",
			authors = ['H. Cassé', "W. McJ. Joseph", "C. Jéré"],
			version="1.0.1",
			description = "Machine level simulator.",
			license = "GPL v3",
			copyright = "Copyright (c) 2023, University of Toulosue 3",
			website="https://github.com/hcasse/bass"

		)

	def new_session(self, man):
		return Session(self, man)

if __name__ == '__main__':
	orc.run(Application(), debug=True)