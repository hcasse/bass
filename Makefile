
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


# docker goals
DOCKER_DIR=tmp/bass
DOCKER_FILES=\
	bass \
	Orchid/orchid \
	Orchid/assets \
	deploy/docker/config.ini
	#armv5t/python/build/lib.linux-x86_64-3.10/armgliss.cpython-310-x86_64-linux-gnu.so
CREATE_USER=$(PWD)/deploy/docker/create_user.py

docker-prepare:
	-rm -rf $(DOCKER_DIR)
	mkdir $(DOCKER_DIR)
	cp -RL $(DOCKER_FILES) $(DOCKER_DIR)
	mkdir $(DOCKER_DIR)/data
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "hugues" "!casse!"
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "thomas" "!carle!"
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "christine" "!rochange!"
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "pascal" "!sainrat!"

docker-base:
	sudo docker build -f deploy/docker/Dockerfile.base -t bass:base .

export DOCKER_BUILDKIT=0
docker:
	cd armv5t; make binclean
	sudo docker build -f deploy/docker/Dockerfile -t bass:latest .

docker-run:
	sudo docker run -p 8888:8888 --name bass --mount type=bind,source=$(abspath $(DOCKER_DIR)/data),target=/bass/data -i -t bass:latest

docker-check:
	sudo docker run -i -t bass:latest bash

docker-stop:
	sudo docker stop bass
	sudo docker-clean -c

# docker exec -ti ID /bin/bash
