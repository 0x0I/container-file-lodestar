filepath        :=      $(PWD)
versionfile     :=      $(filepath)/version.txt
version         :=      $(shell cat $(versionfile))
image_repo      :=      0labs/lodestar
build_type      ?=      package

build:
	DOCKER_BUILDKIT=1 docker build --tag $(image_repo):build-$(version) --build-arg build_type=$(build_type) --build-arg lodestar_version=$(version) .

test:
	DOCKER_BUILDKIT=1 docker build --tag lodestar:test --target test --build-arg build_type=$(build_type) --build-arg lodestar_version=$(version) . && docker run --env-file test/test.env lodestar:test

test-compose-beacon:
	echo "image=${image_repo}:${version}" > compose/.env-test
	cd compose && docker-compose --env-file .env-test config && docker-compose --env-file .env-test up -d lodestar-beacon && \
	sleep 60 && docker-compose logs 2>&1 | grep "Configured for network" && \
	docker-compose logs 2>&1 | grep "prater" && \
	docker-compose logs 2>&1 | grep "Block production enabled" && \
	docker-compose logs 2>&1 | grep "HTTP API started" && \
	docker-compose down && rm .env-test

test-compose-validator:
	echo "image=${image_repo}:${version}" > compose/.env-test
	cd compose && docker-compose --env-file .env-test config && docker-compose --env-file .env-test up -d && \
	sleep 30 && docker-compose logs lodestar-validator 2>&1 | grep "Configured for network" && \
	docker-compose logs lodestar-validator 2>&1 | grep "prater" && \
	docker-compose logs lodestar-validator 2>&1 | grep "Metrics HTTP server started" && \
	docker-compose logs lodestar-validator 2>&1 | grep "Connected to beacon node" && \
	docker-compose down && rm .env-test

release:
	DOCKER_BUILDKIT=1 docker build --tag $(image_repo):$(version) --target release --build-arg build_type=$(build_type) --build-arg lodestar_version=$(version) .
	docker push $(image_repo):$(version)

latest:
	docker tag $(image_repo):$(version) $(image_repo):latest
	docker push $(image_repo):latest

.PHONY: test
