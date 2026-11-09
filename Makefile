PY ?= python3

.PHONY: test
test:
	$(PY) -m pytest -q tests
