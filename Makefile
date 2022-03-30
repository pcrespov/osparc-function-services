.DEFAULT_GOAL := help

.PHONY: hel%
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
hel%:
	@echo "usage: make [target] ..."
	@echo ""
	@echo "Targets for '$(notdir $(CURDIR))':"
	@echo ""
	@awk --posix 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""


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
	pip list 

