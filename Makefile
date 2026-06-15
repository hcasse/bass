
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
ARM_PATH=$(PWD)/armv5t/python
export PYTHONPATH=$(PYTHON_PATH):$(BASS_PATH):$(ORCHID_PATH):$(CSIM_PATH)/python:$(ARM_PATH)


# Rules
all:

run:
	echo "PYTHON_PATH=$(PYTHONPATH)"
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
	@cd armv5t/python; make


# docker goals
DOCKER_DIR=tmp/bass
DOCKER_FILES=\
	bass \
	Orchid/orchid \
	Orchid/assets \
	deploy/docker/config.ini
CREATE_USER=$(PWD)/deploy/docker/create_user.py

docker-prepare:
	sudo rm -rf $(DOCKER_DIR)
	mkdir $(DOCKER_DIR)
	cp armv5t/python/arm_gliss.cpython-*.so $(DOCKER_DIR)/arm_gliss.so
	cp -RL $(DOCKER_FILES) $(DOCKER_DIR)
	mkdir $(DOCKER_DIR)/data
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "hugues" "!casse!" -g teacher
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "thomas" "!carle!" -g teacher
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "christine" "!rochange!" -g teacher
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "pascal" "!sainrat!"  -g teacher
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "loic" "!sylvestre!"  -g teacher
	cd $(DOCKER_DIR); python3 $(CREATE_USER) "admin" "!ADMIN!"

docker-base:
	sudo docker build -f deploy/docker/Dockerfile.base -t bass:base .

export DOCKER_BUILDKIT=0
docker:
	#cd armv5t; make binclean
	sudo docker build -f deploy/docker/Dockerfile -t bass:latest .

docker-run:
	sudo docker run -p 8888:8888 --name bass --mount type=bind,source=$(abspath $(DOCKER_DIR)/data),target=/bass/data -i -t bass:latest

docker-check:
	sudo docker run -i -t bass:latest bash

docker-stop:
	sudo docker stop bass
	sudo docker-clean -c

docker-save:
	sudo docker save bass:latest | gzip > bass.tar.gz
	sudo chown casse:casse bass.tar.gz

docker-clean:
	rm bass.tar.gz


# docker exec -ti ID /bin/bash
