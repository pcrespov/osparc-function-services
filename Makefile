.DEFAULT_GOAL := help


.PHONY: .venv
.venv:
	python -m venv .venv
	.venv/bin/python -m pip install --upgrade pip setuptools wheel
	@echo "To activate the venv, execute 'source .venv/bin/activate'"


.PHONY: install-dev
install-dev: ## install development
	pip install -e ".[test]"


.PHONY: tests
test-dev: # runs tests
	pytest \
		--ff \
        --log-cli-level=INFO \
        --pdb \
        --setup-show \
        -sx \
        -vv \
        tests


.PHONY: info
info: ## general info
	@pip list -v
	# integration tools
	@-python --version
	@-ooil --version
	@-docker --version
	@-docker-compose --version

.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:
	@echo "usage: make [target] ..."
	@echo ""
	@echo "Targets for '$(notdir $(CURDIR))':"
	@echo ""
	@awk --posix 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""


.PHONY: clean clean-force
git_clean_args = -dxf -e .vscode/ -e .venv
clean: ## cleans all unversioned files in project and temp files create by this makefile
	# Cleaning unversioned
	@git clean -n $(git_clean_args)
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo -n "$(shell whoami), are you REALLY sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@git clean $(git_clean_args)



include ./scripts/integration.make
include ./scripts/registry.make