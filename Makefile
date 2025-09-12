.PHONY: help build run stop clean logs shell init-db update-citations dev prod

help: ## Show this help message
	@echo 'Usage: make [target]'
	@echo ''
	@echo 'Available targets:'
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

build: ## Build Docker containers
	docker-compose build

run: ## Run the application in development mode
	docker-compose up -d web

dev: ## Run in development mode with live reload
	docker-compose up web

prod: ## Run in production mode with nginx
	docker-compose --profile production up -d

stop: ## Stop all containers
	docker-compose down

clean: ## Clean up containers and images
	docker-compose down -v
	docker system prune -f

logs: ## View container logs
	docker-compose logs -f

shell: ## Access the Flask container shell
	docker-compose exec web /bin/bash

init-db: ## Initialize the database
	docker-compose exec web sh -c "sqlite3 /app/db/information_.db < /app/db/schema.sql"

update-citations: ## Update citation counts
	docker-compose exec web python citation_update.py

restart: ## Restart containers
	docker-compose restart

status: ## Show container status
	docker-compose ps

backup-db: ## Backup the database
	@mkdir -p backups
	@cp db/information_.db backups/information_$(shell date +%Y%m%d_%H%M%S).db
	@echo "Database backed up to backups/information_$(shell date +%Y%m%d_%H%M%S).db"