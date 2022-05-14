PYTHON=python3

PYTHON_ENV_ROOT=envs
PYTHON_VENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-env
PYTHON_PACKAGING_VENV=$(PYTHON_ENV_ROOT)/$(PYTHON)-packaging-env

.PHONY: clean

# development environment #####################################################
$(PYTHON_VENV)/.created:
	rm -rf $(PYTHON_VENV) && \
	$(PYTHON) -m venv $(PYTHON_VENV) && \
	. $(PYTHON_VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -e . && \
	date > $(PYTHON_VENV)/.created

env: $(PYTHON_VENV)/.created

# packaging environment #######################################################
$(PYTHON_PACKAGING_VENV)/.created: REQUIREMENTS.packaging.txt
	rm -rf $(PYTHON_PACKAGING_VENV) && \
	$(PYTHON) -m venv $(PYTHON_PACKAGING_VENV) && \
	. $(PYTHON_PACKAGING_VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r REQUIREMENTS.packaging.txt
	date > $(PYTHON_PACKAGING_VENV)/.created

packaging-env: $(PYTHON_PACKAGING_VENV)/.created

sdist: packaging-env
	. $(PYTHON_PACKAGING_VENV)/bin/activate && \
	rm -rf dist *.egg-info && \
	./setup.py sdist

_release: sdist
	. $(PYTHON_PACKAGING_VENV)/bin/activate && \
	twine upload --config-file ~/.pypirc.fscherf dist/*

# helper ######################################################################
clean:
	rm -rf $(PYTHON_ENV_ROOT)

envs: env packaging-env

# examples ####################################################################
rlpython: env
	. $(PYTHON_VENV)/bin/activate && \
	. examples/environment.sh && \
	rlpython $(args)

local-embed: env
	. $(PYTHON_VENV)/bin/activate && \
	. examples/environment.sh && \
	python examples/local-embed.py

socket-server: env
	. $(PYTHON_VENV)/bin/activate && \
	. examples/environment.sh && \
	python examples/socket-server.py

multi-session-socket-server: env
	. $(PYTHON_VENV)/bin/activate && \
	. examples/environment.sh && \
	python examples/multi-session-socket-server.py

unix-domain-socket-server: env
	. $(PYTHON_VENV)/bin/activate && \
	. examples/environment.sh && \
	python examples/unix-domain-socket-server.py

