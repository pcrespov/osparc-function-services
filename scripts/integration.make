
.PHONY: install-ooil-local
install-ooil-local: ## install local-version of ooil (for development)
	pip install -e ../osparc-simcore/packages/models-library
	pip install -e ../osparc-simcore/packages/service-integration


.PHONY: install-ooil-head
install-ooil-head: ## install HEAD version of ooil (for development)
	pip install "git+https://github.com/ITISFoundation/osparc-simcore.git@master#egg=simcore-models-library&subdirectory=packages/models-library"
	pip install "git+https://github.com/ITISFoundation/osparc-simcore.git@master#egg=simcore-service-integration&subdirectory=packages/service-integration"


.PHONY: docker-compose.yml
docker-compose.yml: ## (re)create docker-compose
	ooil compose
	#  FIXME: until new version of OOIL includes docker-build override
	sed -i 's/docker\/Dockerfile/Dockerfile/g' $@


.PHONY: build shell push
build: ## docker-compose build
	docker-compose build


shell: ## docker-compose run ... bash
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


push: ## docker-compose push (to registry:5000)
	docker-compose push
