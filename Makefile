.PHONY: help
help:
	@echo "Make targets for lsst-cst:"
	@echo "make clean - Remove generated files"
	@echo "make init - Set up dev environment (install pre-commit hooks)"
	@echo "make linkcheck - Check for broken links in documentation"

.PHONY: clean
clean:
	rm -rf .tox
	rm -rf docs/_build
	rm -rf docs/api

.PHONY: init
init:
	pip install --upgrade pip tox pre-commit
	pip install --upgrade -e ".[dev]"
	pre-commit install
	rm -rf .tox

# This is defined as a Makefile target instead of only a tox command because
# if the command fails we want to cat output.txt, which contains the
# actually useful linkcheck output. tox unfortunately doesn't support this
# level of shell trickery after failed commands.
.PHONY: linkcheck
linkcheck:
	sphinx-build --keep-going -W -T -b linkcheck docs	\
	    docs/_build/linkcheck				\
	    || (cat docs/_build/linkcheck/output.txt; exit 1)
