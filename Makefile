.PHONY: test lint build run
TAG ?= dev

test:
	python3 -I -m unittest discover -s app/tests

lint:
	helm lint chart -f chart/values-staging.yaml
	helm lint chart -f chart/values-prod.yaml
	shellcheck scripts/*.sh

build:
	docker build -t sample:$(TAG) --build-arg APP_VERSION=$(TAG) .

run: build
	docker run --rm -p 8080:8080 sample:$(TAG)
