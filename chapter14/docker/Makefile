build: build-base build-docker

build-base:
	docker build -t airflowbook/chapter14-base-image:latest -f Dockerfile.base .

build-docker:
	docker build -f Dockerfile.base .
