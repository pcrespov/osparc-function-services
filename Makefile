.DEFAULT_GOAL := help

REPODIR_NAME := $(basename $(CURDIR))

.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:
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
	# installing ooil tooling
	pip install "git+https://github.com/ITISFoundation/osparc-simcore.git@master#egg=simcore-models-library&subdirectory=packages/models-library"
	pip install "git+https://github.com/ITISFoundation/osparc-simcore.git@master#egg=simcore-service-integration&subdirectory=packages/service-integration"


.PHONY: docker-compose.yml
docker-compose.yml: ## (re)create docker-compose
	ooil compose


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



.PHONY: build shell
build:
	docker-compose build


shell:
	$(eval TMP := $(shell mktemp -d))
	docker-compose run \
		-u 8004 \
		-e "INPUT_FOLDER=/inputs" \
		-e "OUTPUT_FOLDER=/outputs" \
		--volume $(TMP)/inputs:/inputs \
		--volume $(TMP)/outputs:/outputs \
		--rm \
		ofs-sensitivity_ua_test_func bash
	# cleanup
	@-rm -rf $(TMP)


.PHONY: clean clean-force
git_clean_args = -dxf -e .vscode/ -e .venv
clean: ## cleans all unversioned files in project and temp files create by this makefile
	# Cleaning unversioned
	@git clean -n $(git_clean_args)
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo -n "$(shell whoami), are you REALLY sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@git clean $(git_clean_args)