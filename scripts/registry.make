get_my_ip := $(shell hostname --all-ip-addresses | cut --delimiter=" " --fields=1)

## LOCAL DOCKER REGISTRY (for local development only) -------------------------------


LOCAL_REGISTRY_HOSTNAME := registry
LOCAL_REGISTRY_VOLUME   := $(LOCAL_REGISTRY_HOSTNAME)

.PHONY: registry-%


registry-up:  ## starts a LOCAL docker registry and creates .env to use it (NOTE: needs admin rights)
	@$(if $(shell grep "127.0.0.1 $(LOCAL_REGISTRY_HOSTNAME)" /etc/hosts),,\
					echo configuring host file to redirect $(LOCAL_REGISTRY_HOSTNAME) to 127.0.0.1; \
					sudo echo 127.0.0.1 $(LOCAL_REGISTRY_HOSTNAME) | sudo tee -a /etc/hosts;\
					echo done)
	@$(if $(shell grep "{\"insecure-registries\": \[\"registry:5000\"\]}" /etc/docker/daemon.json),,\
					echo configuring docker engine to use insecure local registry...; \
					sudo echo {\"insecure-registries\": [\"$(LOCAL_REGISTRY_HOSTNAME):5000\"]} | sudo tee -a /etc/docker/daemon.json; \
					echo restarting engine...; \
					sudo service docker restart;\
					echo done)
	@$(if $(shell docker ps --format="{{.Names}}" | grep registry),,\
					echo starting registry on $(LOCAL_REGISTRY_HOSTNAME):5000...; \
					docker run --detach \
							--init \
							--env REGISTRY_STORAGE_DELETE_ENABLED=true \
							--publish 5000:5000 \
							--volume $(LOCAL_REGISTRY_VOLUME):/var/lib/registry \
							--name $(LOCAL_REGISTRY_HOSTNAME) \
							registry:2)

	# WARNING: environment file .env is now setup to use local registry on port 5000 without any security (take care!)...
	@echo "Changes by registry-up recipe in $(CURDIR)" >> .env
	@echo REGISTRY_AUTH=False >> .env
	@echo REGISTRY_SSL=False >> .env
	@echo REGISTRY_PATH=$(LOCAL_REGISTRY_HOSTNAME):5000 >> .env
	@echo REGISTRY_URL=$(get_my_ip):5000 >> .env
	@echo DIRECTOR_REGISTRY_CACHING=False >> .env
	@echo CATALOG_BACKGROUND_TASK_REST_TIME=1 >> .env
	# local registry set in $(LOCAL_REGISTRY_HOSTNAME):5000
	# images currently in registry:
	@sleep 3
	curl --silent $(LOCAL_REGISTRY_HOSTNAME):5000/v2/_catalog | jq '.repositories'

registry-rm: ## remove the registry and changes to host/file
	@$(if $(shell grep "127.0.0.1 $(LOCAL_REGISTRY_HOSTNAME)" /etc/hosts),\
		echo removing entry in /etc/hosts...;\
		sudo sed -i "/127.0.0.1 $(LOCAL_REGISTRY_HOSTNAME)/d" /etc/hosts,\
		echo /etc/hosts is already cleaned)
	@$(if $(shell grep "{\"insecure-registries\": \[\"$(LOCAL_REGISTRY_HOSTNAME):5000\"\]}" /etc/docker/daemon.json),\
		echo removing entry in /etc/docker/daemon.json...;\
		sudo sed -i '/{"insecure-registries": \["$(LOCAL_REGISTRY_HOSTNAME):5000"\]}/d' /etc/docker/daemon.json;,\
		echo /etc/docker/daemon.json is already cleaned)
	# removing container and volume
	-docker rm --force $(LOCAL_REGISTRY_HOSTNAME)
	-docker volume rm $(LOCAL_REGISTRY_VOLUME)


registry-info: ## info on local registry (if any)
	# ping API
	curl --silent $(LOCAL_REGISTRY_HOSTNAME):5000/v2
	# list all
	curl --silent $(LOCAL_REGISTRY_HOSTNAME):5000/v2/_catalog | jq
	# target detail info (if set)
	$(if $(target),\
	@echo Tags for $(target); \
	curl --silent $(LOCAL_REGISTRY_HOSTNAME):5000/v2/$(target)/tags/list | jq ,\
	@echo No target set)
