import subprocess
import bass.arm as config
import os 



def createDiassembly(elfName, nameFile,project):
    cmd= "arm-none-eabi-objdump -d -l '%s' > '%s'" % (elfName,nameFile)
    r= subprocess.run(cmd,shell = True,
				cwd = project,
				encoding = "UTF8",
				capture_output = True)

    supprimer_ligne(nameFile)

def supprimer_ligne(fichier):
    # Lire toutes les lignes du fichier
    with open(fichier, 'r') as f:
        lignes = f.readlines()
    
    # Supprimer la ligne spécifiée
    lignes = [ligne for ligne in lignes if '/' not in ligne.strip()]
    lignes = [ligne for ligne in lignes if 'Dis' not in ligne.strip()]
    lignes = [ligne for ligne in lignes if '' != ligne.strip()]
    lignes = [ligne for ligne in lignes if 'file format' not in ligne.strip()]
    
    # Écrire les lignes restantes dans le fichier
    with open(fichier, 'w') as f:
        f.writelines(lignes)