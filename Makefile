SHELL := /usr/bin/env bash

GIT_SHA1=$(shell git rev-parse HEAD)

.PHONY: whoami
whoami:
	$(call oc_whoami)

.PHONY: install
install: whoami
install:
	@set -euo pipefail; \
	helm dep up ./helm/cas-ciip-2018-extract; \
	helm upgrade --install --atomic --timeout 300s --namespace "$(CIIP_NAMESPACE_PREFIX)-$(ENVIRONMENT)" \
	cas-ciip-2018-extract ./helm/cas-ciip-2018-extract;