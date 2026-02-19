SRC_DIRS = src
PY = python3
MKFILE_PATH := $(abspath $(lastword $(MAKEFILE_LIST)))

#help: PHOLD Param Sweep Makefile
#help: --------------------------
#help: A collection of helpful commands to run for development
#help:
#help: To get started for development, first create a virtual env and then
#help: install the project:
#help:
#help:   ```sh
#help:   python -m venv venv
#help:   source ./venv/bin/activate
#help:   python -m pip install -U pip
#help:   python -m pip install .[dragon,smartsim] --group dev
#help:   ```
#help:
#help:
#help: From there, use the following commands to aid in development:
#help:

.PHONY: help
#help:    help:           Print this help statment
help:
	@echo ''
	@grep "^#help\:" ${MKFILE_PATH} | sed 's/\#help\: \?//'
	@echo ''

.PHONY: import-sort
#help:    import-sort:    Sort imports using `isort`
import-sort:
	@${PY} -m isort ${SRC_DIRS}


.PHONY: format
#help:    format:         Format the project using `black`
format:
	@${PY} -m black ${SRC_DIRS}


.PHONY: style
#help:    style:          Style the project to python standards
style: import-sort format

.PHONY: type-check
#help:    type-check:     Type check the project using `mypy`
type-check:
	@${PY} -m mypy ${SRC_DIRS}
