.DEFAULT_GOAL := help

# From https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: build_citibike_api
build_citibike_api: ## Build the Citi Bike API Docker image
	docker build -t airflowbook/chapter12_citibike_api services/citibike_api

.PHONY: build_citibike_db
build_citibike_db: ## Build the Citi Bike DB Docker image
	docker build -t airflowbook/chapter12_citibike_db services/citibike_db

.PHONY: build_citibike
build_citibike: build_citibike_api build_citibike_db ## Build the Citi Bike API & DB Docker images

.PHONY: build_taxi_fileserver
build_taxi_fileserver: ## Build the NYC Yellow Taxi fileserver Docker image
	docker build -t airflowbook/chapter12_taxi_fileserver services/taxi_fileserver

.PHONY: build_taxi_db
build_taxi_db: ## Build the NYC Yellow Taxi DB Docker image
	docker build -t airflowbook/chapter12_taxi_db services/taxi_db

.PHONY: build_taxi
build_taxi: build_taxi_fileserver build_taxi_db ## Build the NYC Yellow Taxi fileserver & DB Docker images

.PHONY: build_nyc_transportation_api
build_nyc_transportation_api: ## Build NYC Transportation API
	docker build -t airflowbook/chapter12_nyc_transportation_api services/nyc_transportation_api

.PHONY: build_all
build_all: build_citibike build_taxi build_nyc_transportation_api ## Build all Docker images (warning: takes long!)
