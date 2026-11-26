PY ?= python3

.PHONY: setup film radio validate music-brief
setup:
	$(PY) -m venv .venv
	.venv/bin/pip install -r requirements.txt

validate:
	$(PY) -m pipeline.cli validate

radio:
	$(PY) -m pipeline.cli radio

film:
	$(PY) -m pipeline.cli film

music-brief:
	$(PY) -m pipeline.cli music-brief
