.PHONY: up down

CURRENT_HOSTNAME := $(shell hostname)
pass := $(shell grep ^POSTGRES_PASSWORD= .env | cut -d '=' -f 2)

ifeq ($(CURRENT_HOSTNAME), 1738991-cy22118.twc1.net)
    COMPOSE_FILE = docker-compose_prod.yml
else
    COMPOSE_FILE = docker-compose_local.yml
endif

up:
	docker-compose -f $(COMPOSE_FILE) up

build:
	docker-compose -f $(COMPOSE_FILE) up --build

down:
	docker-compose -f $(COMPOSE_FILE) down

bash:
	docker exec -it sublet_bot bash

pg_bash:
	docker exec -it sublet_postgres /bin/sh -c "psql -h postgres -U sayler -d postgres"

logs_report:
	docker logs postgres

debug:
	@echo "Current Hostname: $(CURRENT_HOSTNAME)"
	@echo "Using Compose File: $(COMPOSE_FILE)"
