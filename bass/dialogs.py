"""Other dialog management"""


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

