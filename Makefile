
# Configuration
PYTHON=python3
PYLINT=pylint

# GIT repositories
ORCHID_GIT = https://github.com/hcasse/Orchid.git
GLISS_GIT = https://git.renater.fr/anonscm/git/gliss2/gliss2.git
ARMV5T_GIT = https://git.renater.fr/anonscm/git/gliss2/armv5t.git

# Paths
ORCHID_PATH=$(PWD)/Orchid
CSIM_PATH=$(PWD)/csim
BASS_PATH=$(PWD)
export PYTHONPATH=$(PYTHON_PATH):$(BASS_PATH):$(ORCHID_PATH):$(CSIM_PATH)/python


# Rules
all:

run:
	$(PYTHON) -m bass.server --debug


debug:
	$(PYTHON) -m bass.server --debug-user moi --debug-project=sum --verbose

test:
	$(PYTHON) -m bass.test

check:
	$(PYLINT) bass | less

autodoc:
	gnome-terminal -- pydoc3 -b

setup: git-orchid git-gliss git-armv5t

git-orchid:
	@if [ -e Orchid ]; then \
		echo "Updating orchid"; \
		cd Orchid; git pull; \
	else \
		echo "Downloading orchid"; \
		git clone $(ORCHID_GIT); \
	fi

git-gliss:
	@if [ -e gliss2 ]; then \
		echo "Updating gliss"; \
		cd gliss2; git pull; \
	else \
		echo "Downloading gliss"; \
		git clone $(GLISS_GIT); \
	fi
	@cd gliss2; make

git-armv5t:
	@if [ -e armv5t ]; then \
		echo "Updating ArmV5T"; \
		cd armv5t; git pull; \
	else \
		echo "Downloading ArmV5T"; \
		git clone $(ARMV5T_GIT); \
		cd armv5t; \
		make config.mk; \
		echo "WITH_PYTHON = 1" >> config.mk; \
		echo "WITH_IO = 1" >> config.mk; \
	fi
	@cd armv5t; make
	@cd armv5t/python; $(PYTHON) setup.py install --user


