REGISTRY := ghcr.io
OWNER := thombashi
REPO := elasticsearch-faker

VERSION := $(shell ./extract_version.sh)


.PHONY: check-github-token
check-github-token:
ifndef GITHUB_TOKEN
	$(error require GITHUB_TOKEN)
endif

.PHONY: docker-login
docker-login: check-github-token
	@echo $(GITHUB_TOKEN) | docker login $(REGISTRY) -u $(OWNER) --password-stdin

.PHONY: docker-build
docker-build:
	docker build -t $(REGISTRY)/$(OWNER)/$(REPO):v$(VERSION) --pull . --build-arg version=$(VERSION)

.PHONY: docker-push
docker-push:
	docker push $(REGISTRY)/$(OWNER)/$(REPO):v$(VERSION)
