PYTHON=python3
PYTHON_VENV=env
PYTHON_PACKAGING_VENV=env-packaging

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

clean:
	rm -rf $(PYTHON_VENV)

# packaging ###################################################################
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
