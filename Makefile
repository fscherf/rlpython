PYTHON=python3
PYTHON_VENV=env

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
sdist:
	rm -rf dist *.egg-info && \
	./setup.py sdist
