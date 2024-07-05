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

		# Hmmm
		self.msgError = None
		self.layeredError = None
		self.dialogError = None
		self.layeredErrorConnection = None
		self.dialogErrorConnection = None
		self.dialogDeconnexion = None
		self.fieldMdp = None
		self.fieldEmail = None
		self.layeredDeconnexion = None
		self.connectButton = None
		self.username = None
		self.mdp = None
		self.buttonNewAccount = None
		self.lcreercompte = None
		self.buttonforgotPassword = None
		self.lforgotpassword = None
		self.layeredConnexion = None
		self.dialog_connexion = None
		self.fieldNom = None
		self.fieldnewUSername = None
		self.fieldnewMdp = None
		self.buttonCreate = None
		self.groupUtilaccount = None
		self.newusername = None
		self.newmdp = None
		self.newNom = None
		self.newlayeredConnexion = None
		self.dialognewAccount = None
		self.fieldRetrieveAccount = None
		self.layeredRetrieve = None
		self.dialogforgotPassword = None
		self.currentFint = None
		self.currentTab = None
		self.currentFile = None
		self.fieldFileName = None
		self.layeredRenameFichier = None

	def get_user(self):
		return self.user

	def start_sim(self):
		"""Start the simulation."""
		if self.user.id == -1:
			self.event_errorConnection()
		else:
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
					self.consoleMemory.clear()
					self.print_Disassembly()
					#self.print_Memory()
				except bass.SimException as e:
					self.console.append(orc.text(orc.ERROR, "ERROR:") + str(e))

	def stop_sim(self):
		"""Stop the current simulation."""
		if self.user.id == -1:
			self.event_errorConnection()
		else:
			self.enable_sim(False)
			self.console.append(orc.text(orc.INFO, "Stop simulation."))
			self.sim.release()
			self.sim = None

	def playstop(self):
		if self.sim is not None:
			self.stop_sim()
		else:
			self.start_sim()

	def step(self):
		#print("Simulateur ",self.sim)
		self.sim.stepInto()
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
		else:
			self.console.append(orc.text(orc.SUCCESS, "SUCCESS!"))

	def print_line(self, line):
		m = LINE_RE.match(line)
		if m is not None:
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


	#---------------------dialog----------------------------#
	def createDialog(self):
		pass
		#self.make_dialog_connexion()
		#self.make_dialog_error()
		#self.make_dialog_Newaccount()
		#self.make_dialog_forgotPassword()
		#self.make_dialog_renameProject()
		#self.make_dialog_renameFile()
		#self.make_dialog_removeProject()
		#self.make_dialog_removeFile()
		#self.make_dialog_securityRemoveProject()
		#self.make_dialog_securityRemoveFile()
		#self.make_dialog_errorConnection()
		#self.make_dialogDeconnexion()

	#-------event_error--------------------------------------#
	def event_error(self, texte):
		"""
			Fonction permettant de creer une fenetre de dialogue d'erreurs.

			  @param texte : Le texte d'erreur a afficher dans la fenetre de dialogue d'erreurs.
		"""
		self.make_dialog_error(texte)
		self.dialogError.show()

	def event_cancelError(self):
		"""
			Fonction permettant de faire disparaitre la fenetre de dialogue d'erreurs.
		"""
		self.dialogError.hide()

	def layeredErroR(self, texte):
		"""
			Fonction permettant de creer le contenue d'une fenetre de dialogue
			servant a la gestion des messages d'erreurs.

			  @param texte : Le message d'erreur qui sera contenu par la fenetre
			  de dialogue.
		"""
		self.msgError = orc.HGroup([orc.Label(texte)])
		self.layeredError = orc.LayeredPane([
			orc.VGroup([
				self.msgError,
				orc.Spring(hexpand=True),
				orc.Button("Ok", on_click=self.event_cancelError)
			])
		])
		self.layeredError.weight = 10

	def make_dialog_error(self, texte=""):
		"""
			Fonction permettant de creer une fenetre de dialogue pour la gestion des messages erreurs.

			  @param texte : Le message d'erreur qui sera contenu par la fenetre de dialogue.
		"""
		self.layeredErroR(texte)
		self.dialogError = dialog.Base(self.page, self.layeredError)
	#------------------------------------------------------#

	#------------event_error_connection--------------------#
	def event_errorConnection(self):
		"""Error.
		"""
		self.make_dialog_errorConnection()
		self.dialogErrorConnection.show()

	def event_cancelErrorConnection(self):
		"""Cancel.
		"""
		self.dialogErrorConnection.hide()
	def layeredErroRConnection(self):
		"""Error.
		"""
		self.layeredErrorConnection = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Label("Vous ne pouvez pas faire cette action sans être \
						connecté !")]),
					orc.Spring(vexpand=True),
					orc.HGroup([
						orc.Button("Annuler l'action",
							on_click=self.event_cancelErrorConnection),
						orc.Spring(hexpand=True),
						orc.Button("Se Connecter",
							on_click=self.event_connexion)
					])
				])
			])
		self.layeredErrorConnection.weight = 15
	def make_dialog_errorConnection(self):
		"""Error.
		"""
		self.layeredErroRConnection()
		self.dialogErrorConnection = dialog.Base(self.page, self.layeredErrorConnection)


	def eventDisconnect(self):
		self.dialogDeconnexion.hide()
	def layeredDeconnexionDialog(self):
		self.layeredDeconnexion= orc.LayeredPane([
			orc.Button("Disconnect", on_click= self.eventDisconnect)
		])
		self.layeredDeconnexion.weight=10
	def make_dialogDeconnexion(self):
		"""
			Event handler to create the dialog (deconnexion).
		"""
		self.layeredDeconnexionDialog()
		self.dialogDeconnexion= dialog.Base(self.page,self.layeredDeconnexion)


	#------------------------------------------------------#

	#------------------CAs connecter------------------------
	def event_connexion(self):
		self.make_dialog_connexion()
		self.dialog_connexion.show()
		self.dialogErrorConnection.hide()

	def event_connected(self):
		self.dialog_connexion.hide()

	def layeredconnexionDialog(self):
		self.fieldEmail= orc.EmailField(size=20)
		self.fieldMdp= orc.PasswordField(size=20)
		self.connectButton= orc.Button("connect", on_click=self.login_user)
		self.username= orc.HGroup([
			orc.Label("Email"),
			orc.Spring(hexpand=True),
			self.fieldEmail,
			self.connectButton
		])
		self.mdp= orc.HGroup([
			orc.Label("Password"),
			orc.Spring(hexpand=True),
			self.fieldMdp
		])

		self.buttonNewAccount= orc.Button("New Account",
			on_click= self.eventCreateAccount)
		self.lcreercompte= orc.HGroup([
			orc.Label("Don't have an account"),
			orc.Spring(hexpand=True),
			self.buttonNewAccount
		])
		self.buttonforgotPassword= orc.Button("Retrieve",
			on_click= self.event_forgotPassword)
		self.lforgotpassword=orc.HGroup([
			orc.Label("Retrieve"),
			orc.Spring(hexpand=True),
			self.buttonforgotPassword
		])
		self.layeredConnexion= orc.LayeredPane([
			orc.VGroup([
				self.username,
				self.mdp,
				orc.Spring(vexpand=True),
				self.lcreercompte,
				orc.Spring(vexpand=True),
				self.lforgotpassword,
				self.buttonCancel
			])
		])
		self.layeredConnexion.weight=10

	def make_dialog_connexion(self):
		self.layeredconnexionDialog()
		self.dialog_connexion=dialog.Base(self.page, self.layeredConnexion)
	#------------------------------------------------

	#-----------creer compte-------------------------
	def eventCreateAccount(self):
		self.make_dialog_Newaccount()
		self.dialognewAccount.show()

	def event_accountCreated(self):
		self.dialog_connexion.hide()
		self.dialognewAccount.hide()
		self.sigin()

	def layeredCreateAcountDialog(self):
		self.fieldNom= orc.Field(size=20)
		self.fieldnewUSername= orc.EmailField(size=20)
		self.fieldnewMdp= orc.PasswordField(size=20)
		self.buttonCreate= orc.Button("create",
			on_click= self.event_accountCreated)
		self.groupUtilaccount= orc.HGroup([
			self.buttonCreate,
			orc.Spring(hexpand=True),
			self.buttonCancel
		])
		self.newusername= orc.HGroup([
			orc.Label("Email"),
			orc.Spring(hexpand=True),
			self.fieldEmail
		])
		self.newmdp= orc.HGroup([
			orc.Label("Password"),
			orc.Spring(hexpand=True),
			self.fieldMdp
		])
		self.newNom= orc.HGroup([
			orc.Label("Username"),
			orc.Spring(hexpand=True),
			self.fieldNom
		])
		self.newlayeredConnexion= orc.LayeredPane([
			orc.VGroup([
				self.newusername,
				self.newNom,
				self.newmdp,
				orc.Spring(vexpand=True),
				self.groupUtilaccount
			])
		])
		self.newlayeredConnexion.weight=10

	def make_dialog_Newaccount(self):
		self.layeredCreateAcountDialog()
		self.dialognewAccount= dialog.Base(self.page, self.newlayeredConnexion)
	#--------------------------------------------------#

	#----------------------mot de passe oublie----------#
	def event_forgotPassword(self):
		self.dialogforgotPassword.show()

	def cancelforgotPasswordEvent(self):
		self.dialogforgotPassword.hide()

	def event_submitForgotPassword(self):
		self.dialog_connexion.hide()
		self.dialognewAccount.hide()
		self.dialogforgotPassword.hide()

	def layeredforgotPassword(self):
		self.fieldRetrieveAccount= orc.EmailField(size=20)
		self.layeredRetrieve= orc.LayeredPane([
			orc.HGroup([
				orc.Label("Email"),
				orc.Spring(hexpand=True),
				self.fieldRetrieveAccount,
				orc.Button("Submit", on_click=self.event_submitForgotPassword),
				orc.Button("cancel",on_click=self.event_full_hide_dialogs)
			])
		])

	def make_dialog_forgotPassword(self):
		self.layeredforgotPassword()
		self.dialogforgotPassword=dialog.Base(self.page, self.layeredRetrieve)
	#---------------------------------------------#

	def event_full_hide_dialogs(self):
		self.dialog_connexion.hide()
		self.dialogforgotPassword.hide()
		self.dialognewAccount.hide()

	#-------rename_file-------#
	def event_renameFile(self):
		"""Rename.
		"""
		if self.user.id == -1:
			self.event_errorConnection()
		else:
			self.currentFint = self.tabEditeurDisassembly.current
			self.currentTab = self.tabEditeurDisassembly.tabs[self.currentFint]
			self.currentFile = self.user.projects[self.currentProject].files[self.currentFint-1]
			self.saveAll()
			self.make_dialog_renameFile( self.currentFile.name )
			self.dialogRenameFile.show()

	def event_hideRenameFile(self):
		"""Rename.
		"""
		self.dialogRenameFile.hide()

	def layeredRenameFile(self, filename):
		"""Rename.
		"""
		self.fieldFileName = orc.Field(size=20, init=filename)
		self.layeredRenameFichier = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Label("Entrez le nouveau nom du fichier : ")
				]),
				orc.HGroup([
					orc.Spring(hexpand=True),
					self.fieldFileName
				]),
				orc.Spring(vexpand=True),
				orc.HGroup([
					orc.Button("Annuler", on_click = self.event_hideRenameFile),
					orc.Spring(hexpand=True),
					orc.Button("Valider", on_click= self.renameFile)
				])
			])
		])
		self.layeredRenameFichier.weight = 20

	def make_dialog_renameFile(self, texte=""):
		"""Rename.
		"""
		self.layeredRenameFile(texte)
		self.dialogRenameFile = dialog.Base(self.page, self.layeredRenameFichier)
	#-------------------------#

	#------rename_project------#
	def event_renameProject(self):
		"""Rename.
		"""
		if self.user.id == -1:
			self.event_errorConnection()
		else:
			self.currentFint = self.tabEditeurDisassembly.current
			self.saveAll()
			self.make_dialog_renameProject(texte = self.user.projects[self.currentProject].name)
			self.dialogRenameProject.show()

	def event_hideRenameProject(self):
		"""Hide.
		"""
		self.dialogRenameProject.hide()

	def layeredRenameProject(self, projectname):
		"""Rename.
		"""
		self.fieldProjectName = orc.Field(size=20, init=projectname)
		self.layeredRenameProjet = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Label("Entrez le nouveau nom du projet : ")]),
					orc.HGroup([orc.Spring(hexpand=True),
					self.fieldProjectName
				]),
				orc.Spring(vexpand=True),
				orc.HGroup([
					orc.Button("Annuler", on_click = self.event_hideRenameProject),
					orc.Spring(hexpand=True),
					orc.Button("Valider", on_click= self.renameProject)
				])
			])
		])
		self.layeredRenameProjet.weight = 20

	def make_dialog_renameProject(self, texte = ""):
		"""Rename.
		"""
		self.layeredRenameProject(texte)
		self.dialogRenameProject = dialog.Base(self.page, self.layeredRenameProjet)
	#----------------------------------------------------#

	#------remove_file------#
	def event_removeFile(self):
		"""Remove.
		"""
		if self.user.id == -1:
			self.event_errorConnection()
		else:
			self.currentFint = self.tabEditeurDisassembly.current
			#self.currentTab = self.tabEditeurDisassembly[self.currentFint]
			#self.currentFile = self.user.projects[self.currentProject][self.currentFint-1]
			self.saveAll()
			self.make_dialog_removeFile(self.user.projects[self.currentProject]\
				.files[self.currentFint-1].name )
			self.dialogRemoveFile.show()

	def event_hideRemoveFile(self):
		"""Remove.
		"""
		self.dialogRemoveFile.hide()

	def layeredRemoveFile(self, filename):
		"""Remove.
		"""
		self.layeredRemoveFichier = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Spring(hexpand=True),
					orc.Label(f"Voulez vous vraiment supprimer définitivement \
						le fichier {filename} ?"),
					orc.Spring(hexpand=True)
				]),
				orc.Spring(vexpand=True),
				orc.HGroup([
					orc.Button("Non ! Annuler", on_click=self.event_hideRemoveFile),
					orc.Spring(hexpand=True),
					orc.Button("Oui, valider", on_click=self.event_securityRemoveFile)
				])
			])
		])
		self.layeredRemoveFichier.weight = 10

	def make_dialog_removeFile(self, texte = ""):
		"""Remove.
		"""
		self.layeredRemoveFile(texte)
		self.dialogRemoveFile = dialog.Base(self.page, self.layeredRemoveFichier)

	def event_securityRemoveFile(self):
		self.make_dialog_securityRemoveFile()
		self.dialogSecurityRemoveFile.show()

	def event_hideSecurityRemoveFile(self):
		self.dialogSecurityRemoveFile.hide()
		self.dialogRemoveFile.hide()

	def layeredSecurityRemoveFile(self):
		self.fieldMdp = orc.PasswordField(size=20)
		#self.fieldMdp.set_content(" ")
		self.layeredSecurityRemoveFichier = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Label("Pour confirmer la suppression, \
						Veuillez entrer votre mot de passe : "),
					orc.Spring(hexpand=True)
				]),
				orc.HGroup([
					orc.Spring(hexpand=True),
					self.fieldMdp
				]),
				orc.Spring(vexpand=True),
				orc.HGroup([
					orc.Button("Annuler", on_click=self.event_hideSecurityRemoveFile),
					orc.Spring(hexpand=True),
					orc.Button("Valider", on_click=self.removeFile)
				])
			])
		])
		self.layeredSecurityRemoveFichier.weight = 10

	def make_dialog_securityRemoveFile(self):
		"""Security.
		"""
		self.layeredSecurityRemoveFile()
		self.dialogSecurityRemoveFile = dialog.Base(self.page, self.layeredSecurityRemoveFichier)

	def removeFile(self):
		"""Remove.
		"""
		data = pd.read_csv(os.path.join(config.DATADIR,"account.txt"))
		#line = df.loc[df['id']==idUser]
		#data = data.loc[data['id']==self.user.id]
		mdpCourant = data.iloc[0, 3]
		if mdpCourant != self.fieldMdp.get_value():
			self.event_error("Le mot de passe est incorrecte.")
		else:
			self.user.projects[self.currentProject].files[self.currentFint-1].delete()
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
			self.event_hideSecurityRemoveFile()
	#----------------------------------------------------#

	#------remove_project------#
	def event_removeProject(self):
		"""Remove.
		"""
		if self.user.id == -1:
			self.event_errorConnection()
		else:
			self.currentFint = self.tabEditeurDisassembly.current
			#self.currentTab = self.tabEditeurDisassembly[self.currentFint]
			#self.currentProject = self.user.projects[self.currentProject][self.currentFint-1]
			self.saveAll()
			self.make_dialog_removeProject( self.user.projects[self.currentProject].name )
			self.dialogRemoveProject.show()

	def event_hideRemoveProject(self):
		"""Remove.
		"""
		self.dialogRemoveProject.hide()

	def layeredRemoveProject(self, projectname):
		"""Remove.
		"""
		self.layeredRemoveProjet = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Spring(hexpand=True),
					orc.Label(f"Voulez vous vraiment supprimer définitivement \
						le projet {projectname} et tout les fichiers qu'il contient ?"),
					orc.Spring(hexpand=True)
				]),
				orc.Spring(vexpand=True),
				orc.HGroup([
					orc.Button("Non ! Annuler", on_click=self.event_hideRemoveProject),
					orc.Spring(hexpand=True),
					orc.Button("Oui, valider", on_click=self.event_securityRemoveProject)
				])
			])
		])
		self.layeredRemoveProjet.weight = 10

	def make_dialog_removeProject(self, texte = ""):
		"""Remove.
		"""
		self.layeredRemoveProject(texte)
		self.dialogRemoveProject = dialog.Base(self.page, self.layeredRemoveProjet)

	def event_securityRemoveProject(self):
		self.make_dialog_securityRemoveProject()
		self.dialogSecurityRemoveProject.show()

	def event_hideSecurityRemoveProject(self):
		self.dialogSecurityRemoveProject.hide()
		self.dialogRemoveProject.hide()

	def layeredSecurityRemoveProject(self):
		self.fieldMdp = orc.PasswordField(size=20)
		#self.fieldMdp.set_content(" ")
		self.layeredSecurityRemoveProjet = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Label("Pour confirmer la suppression, \
						Veuillez entrer votre mot de passe : "),
					orc.Spring(hexpand=True)
				]),
				orc.HGroup([
					orc.Spring(hexpand=True),
					self.fieldMdp
				]),
				orc.Spring(vexpand=True),
				orc.HGroup([orc.Button("Annuler",
					on_click=self.event_hideSecurityRemoveProject),
					orc.Spring(hexpand=True),
					orc.Button("Valider", on_click=self.removeProject)
				])
			])
		])
		self.layeredSecurityRemoveProjet.weight = 10

	def make_dialog_securityRemoveProject(self):
		"""Remove.
		"""
		self.layeredSecurityRemoveProject()
		self.dialogSecurityRemoveProject = dialog.Base(self.page, self.layeredSecurityRemoveProjet)

	def removeProject(self):
		"""Remove.
		"""
		#df = pd.read_csv( os.path.join(config.DATADIR,"account.txt") )
		#line = df.loc[df['id']==self.user.id]
		mdpCourant = ""	# line.iloc[0, 3]
		if mdpCourant != self.fieldMdp.get_value():
			self.event_error("Le mot de passe est incorrecte.")
		else:
			self.user.projects[self.currentProject].delete_project()
			self.user.remove_project(self.user.projects[self.currentProject])
			self.loadProjectsGroup()
			# if (len(self.user.projects) > 0):
			self.loadProjectFilesEditor()
			# else:
				#Affichage du message invitant à créer un projet
			self.event_hideSecurityRemoveProject()
	#----------------------------------------------------#

	#---------template_projet-----------------#
	def event_templateProject(self):
		if self.user.id == -1:
			self.event_errorConnection()
		else:
			self.saveAll()
			self.make_dialog_choiceTemplateProject()
			self.dialogChoiceTemplateProject.show()

	def event_hideChoiceProject(self):
		self.dialogChoiceTemplateProject.hide()

	def makeButtonLambdaTemplateProject(self, project):
		return orc.Button(project.name, on_click=lambda : self.event_validTemplateProject(project))

	def layeredChoiceTemplateProject(self):
		tPath = os.path.join(config.DATADIR, str(0))
		lH = []
		lV = []
		cpt = 0
		titre = orc.Label("Choisissez la template de projet de votre choix : ")
		lV.append(orc.HGroup([
			orc.Spring(hexpand=True),
			titre,
			orc.Spring(hexpand=True),
			orc.Spring(hexpand=True),
			orc.Button("Annuler", on_click=self.event_hideChoiceProject)
		]))
		for p in os.listdir(tPath):
			dirPath = os.path.join(tPath, p)
			if not os.path.isfile(dirPath):
				project = Project(self.user, name = p)
				project.load()
				if cpt == 3:
					lV.append(orc.HGroup(lH))
					lH = []
					cpt = 0
					lH.append(orc.Spring(hexpand=True))
				lH.append(self.makeButtonLambdaTemplateProject(project))
				lH.append(orc.Spring(hexpand=True))
				cpt += 1
		lV.append(orc.HGroup(lH))
		self.layeredChoixTemplateProjet = orc.LayeredPane([orc.VGroup(lV)])
		self.layeredChoixTemplateProjet.weight = 20

	def make_dialog_choiceTemplateProject(self):
		self.layeredChoiceTemplateProject()
		self.dialogChoiceTemplateProject = dialog.Base(self.page, self.layeredChoixTemplateProjet)

	def event_validTemplateProject(self, project):
		self.make_dialog_validTemplateProject(project)
		self.dialogValidTemplateProject.show()

	def event_hideValidTemplateProject(self):
		self.dialogValidTemplateProject.hide()

	def layeredValidTemplateProject(self, project):
		l = []
		for f in project.files:
			if ".s" in f.name and ".elf" not in f.name:
				#l.append(MyTabEditor(f.name, orc.Editor(init =
				#	f.loadWithPath( os.path.join(config.DATADIR, str(0), project.name, f.name)))))
				pass
		self.layeredValidTemplateProjet = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Label("Voici le projet que vous avez selectionné :")
				]),
				orc.TabbedPane(l),
				orc.HGroup([
					orc.Button("Annuler l'ajout", on_click=self.event_hideValidTemplateProject),
					orc.Spring(hexpand=True),
					orc.Button("Ajouter le projet",
					on_click=lambda: self.event_ValidNameTemplateProject(project))
				])
			])
		])
		self.layeredValidTemplateProjet.weight = 20

	def make_dialog_validTemplateProject(self, project):
		self.layeredValidTemplateProject(project)
		self.dialogValidTemplateProject = dialog.Base(self.page, self.layeredValidTemplateProjet)

	def event_ValidNameTemplateProject(self, project):
		self.make_dialog_validNameTemplateProject(project)
		self.dialogValidNameTemplateProject.show()

	def event_hideValidNameTemplateProject(self):
		self.dialogValidNameTemplateProject.hide()

	def layeredValidNameTemplateProject(self, project):
		self.fieldProjectName = orc.Field(size=20, init=project.name)
		self.layeredValidNameTemplateProjet = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Label("Entrez le nouveau nom du projet : ")
				]),
				orc.HGroup([
					orc.Spring(hexpand=True),
					self.fieldProjectName
				]),
				orc.Spring(vexpand=True),
				orc.HGroup([
					orc.Button("Annuler", on_click = self.event_hideValidNameTemplateProject),
					orc.Spring(hexpand=True),
					orc.Button("Valider", on_click=lambda: self.addProject(project))
				])
			])
		])
		self.layeredValidNameTemplateProjet.weight = 20

	def make_dialog_validNameTemplateProject(self, project):
		self.layeredValidNameTemplateProject(project)
		self.dialogValidNameTemplateProject = dialog.Base(self.page, self.layeredValidNameTemplateProjet)


	#---------template_Fichier-----------------#
	def event_templateFile(self):
		if self.user.id == -1:
			self.event_errorConnection()
		else:
			self.saveAll()
			self.make_dialog_choiceTemplateFile()
			self.dialogChoiceTemplateFile.show()

	def event_hideChoiceFile(self):
		self.dialogChoiceTemplateFile.hide()

	def makeButtonLambdaTemplateFile(self, texte, file):
		return orc.Button(texte, on_click=lambda: self.event_validTemplateFile(file))

	def layeredChoiceTemplateFile(self):
		#tPath = os.path.join(config.DATADIR, str(0))
		lH = []
		lV = []
		cpt = 0
		#i = 0
		titre = orc.Label("Choisissez la template de fichier de votre choix : ")
		lV.append(orc.HGroup([
			orc.Spring(hexpand=True),
			titre,
			orc.Spring(hexpand=True),
			orc.Spring(hexpand=True),
			orc.Button("Annuler", on_click=self.event_hideChoiceFile)
		]))
		tempSys = User(self.app, "")
		tempSys.load()
		for p in tempSys.projects:
			for f in p.files:
				if cpt == 3:
					lV.append(orc.HGroup(lH))
					lH = []
					cpt = 0
					lH.append(orc.Spring(hexpand=True))
				lH.append(self.makeButtonLambdaTemplateFile(p.name+"/"+f.name, f))
				lH.append(orc.Spring(hexpand=True))
				cpt += 1
		lV.append(orc.HGroup(lH))
		self.layeredChoixTemplateFichier = orc.LayeredPane([orc.VGroup(lV)])
		self.layeredChoixTemplateFichier.weight = 20

	def make_dialog_choiceTemplateFile(self):
		self.layeredChoiceTemplateFile()
		self.dialogChoiceTemplateFile = dialog.Base(self.page, self.layeredChoixTemplateFichier)

	def event_validTemplateFile(self, file):
		self.make_dialog_validTemplateFile(file)
		self.dialogValidTemplateFile.show()

	def event_hideValidTemplateFile(self):
		self.dialogValidTemplateFile.hide()

	def layeredValidTemplateFile(self, file):
		self.editorTempFile = orc.Editor(init = file.load())
		self.layeredValidTemplateFichier = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Label("Voici le fichier que vous avez selectionné :")
				]),
				orc.TabbedPane([
					MyTabEditor(file.get_name(), self.editorTempFile)
				]),
				orc.HGroup([
					orc.Button("Annuler l'ajout", on_click=self.event_hideValidTemplateFile),
					orc.Spring(hexpand=True),
					orc.Button("Ajouter le fichier", on_click=lambda: self.event_ValidNameTemplateFile(file))
				])
			])
		])
		self.layeredValidTemplateFichier.weight = 20

	def make_dialog_validTemplateFile(self, file):
		self.layeredValidTemplateFile(file)
		self.dialogValidTemplateFile = dialog.Base(self.page, self.layeredValidTemplateFichier)

	def event_ValidNameTemplateFile(self, file):
		self.make_dialog_validNameTemplateFile(file)
		self.dialogValidNameTemplateFile.show()

	def event_hideValidNameTemplateFile(self):
		self.dialogValidNameTemplateFile.hide()

	def layeredValidNameTemplateFile(self, file):
		self.fieldFileName = orc.Field(size=20, init=file.name)
		self.layeredValidNameTemplateFichier = orc.LayeredPane([
			orc.VGroup([
				orc.HGroup([
					orc.Label("Entrez le nouveau nom du fichier : ")
				]),
				orc.HGroup([
					orc.Spring(hexpand=True),
					self.fieldFileName
				]),
				orc.Spring(vexpand=True),
				orc.HGroup([
					orc.Button("Annuler", on_click = self.event_hideValidNameTemplateFile),
					orc.Spring(hexpand=True),
					orc.Button("Valider", on_click=lambda: self.addFile(file))
				])
			])
		])
		self.layeredValidNameTemplateFichier.weight = 20

	def make_dialog_validNameTemplateFile(self, file):
		self.layeredValidNameTemplateFile(file)
		self.dialogValidNameTemplateFile = dialog.Base(self.page, self.layeredValidNameTemplateFichier)


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

	#def loadProjectsGroup(self):
	#	""" sdf """
	#	for i in range(len(self.projectsGroup.get_children())-4):
	#		self.projectsGroup.remove(len(self.projectsGroup.get_children())-1)
	#	hIntern=[]
	#	hIntern.append(orc.Spring(hexpand=True))
	#	for i in range(len(self.user.projects)):
	#	if (i%3 == 0 and i!=0):
	#			self.projectsGroup.insert( orc.HGroup(hIntern) )
	#			hIntern = []
	#			hIntern.append(orc.Spring(hexpand=True))
	#		but = self.makeButtonLambdaProject(i)
	#		hIntern.append(but)
	#		hIntern.append(orc.Spring(hexpand=True))
	#	self.projectsGroup.insert( orc.HGroup(hIntern) )

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

	def sigin(self):
		"""
			La fonction qui recupere dans la fenetre de dialogue les informations
			entrees par l'utilisateur, et permet de creer un compte, tout en
			gerant les exceptions.
		"""
		#name = self.fieldNom.get_value()
		#email = self.fieldEmail.get_value()
		#mdp = self.fieldMdp.get_value()
		#if (','in email or ',' in mdp or ',' in name):
		#	text = "Le caractere special , est interdit."
		#	self.event_error(text)
		#data = pd.read_csv(os.path.join(config.DATADIR,"account.txt"))
		#listID = set(data['id'])
		#if data.loc[data['email'] == email].size != 0:
		#	text = "Un compte existe deja pour cette adresse email."
		#	self.event_error(text)
		#else:
		#	self.user.sigUser(name, email, mdp)
		#	self.login()
		#	self.event_accountCreated()



	def get_index(self):

		self.user_label = orc.Label("")
		self.user_label.set_style("min-width", "8em")
		self.project_label = orc.Label("")
		self.project_label.set_style("min-width", "8em")

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
		self.editors = []

		# initialize console
		self.console = orc.Console(init = "<b>Welcome to BASS!</b>\n")

		#-----------editeur + disassembly console -----------
		self.num = 0
		self.cnt = 2

		self.consoleDis=orc.Console(init="Disassembly")

		#self.tabEditeurDisassembly = orc.TabbedPane([
		#	MyTabConsole("Disassembly", self.consoleDis),
		#	MyTabEditor("main.s", CodeEditor(text = ""), None)
		#])


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
				orc.Button("Ajouter un nouveau projet",
					on_click=self.event_templateProject)]),
				orc.Spring(vexpand=True)
		]
		l.extend(hlist)
		self.projectsGroup = orc.VGroup(l)

		self.tabMemoryProjet=orc.TabbedPane([
			MyTabConsole("Memory",self.consoleMemory),
			MyTabConsole("Projets",self.projectsGroup)
		])
		self.memoryConsoleGroup=orc.VGroup([self.tabMemoryProjet,self.console])

		# generate the page
		self.register_pane = RegisterPane()
		self.editor_pane = EditorPane()
		self.page = orc.Page(
			orc.VGroup([
				orc.Header("BASS", [
					orc.Button(image = orc.Icon("box")),
					self.project_label,
					orc.Button(image = orc.Icon("person"), 			on_click=self.event_connexion),
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
					orc.Button(orc.Icon("help"), on_click=self.help),
					orc.Button(orc.Icon("about"), on_click=self.about)
				]),
				orc.HGroup([
					self.register_pane,
					orc.VGroup([
						#orc.HGroup([
						#	orc.Button("Nouveau fichier", on_click=self.event_templateFile),
						#	orc.Button("Supprimer le fichier", on_click=self.event_removeFile),
						#	orc.Button("Renommer le fichier", on_click=self.event_renameFile),
						#	orc.Button("first", on_click=self.first),
						#	orc.Spring(hexpand=True),
						#	orc.Button("Save All", on_click=self.saveAll),
						#	orc.Button("Renommer le Projet", on_click=self.event_renameProject),
						#	orc.Button("Supprimer le Projet", on_click=self.event_removeProject)
						#]),
					self.editor_pane
				]),
				self.memoryConsoleGroup
				])
			]),
			app = self.get_application()
		)

		# build dialogs
		self.buttonCancel= orc.Button("cancel", on_click=self.event_full_hide_dialogs)
		self.createDialog()

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
