.PHONY: all-checks mcp-health install clean

# Run all quality checks
all-checks:
	@echo "Running all quality checks..."
	npm run lint
	npm run typecheck
	npm run test
	npm run build
	npm run security:audit
	npm run security:headers
	npm run performance:lighthouse
	npm run performance:axe
	npm run load:smoke
	npm run mcp:validate
	npm run mcp:health
	@echo "All checks completed successfully!"

# Check MCP server health
mcp-health:
	@echo "Checking MCP server health..."
	npm run mcp:health

# Install dependencies
install:
	@echo "Installing dependencies..."
	npm install
	cd apps/web && npm install
	cd packages/ui && npm install
	cd packages/types && npm install

# Clean build artifacts
clean:
	@echo "Cleaning build artifacts..."
	npm run clean
	rm -rf node_modules
	rm -rf apps/*/node_modules
	rm -rf packages/*/node_modules
	rm -rf .next
	rm -rf dist
	rm -rf coverage
	rm -rf test-results
	rm -rf playwright-report

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	cp .env.example .env.local
	@echo "Please update .env.local with your configuration"

# Production build
prod-build:
	@echo "Building for production..."
	npm run build
	npm run test:e2e
	npm run security:audit
	npm run performance:lighthouse

# Docker development stack
docker-dev:
	@echo "Starting development stack..."
	docker-compose -f infra/docker/compose.dev.yml up -d

# Stop development stack
docker-stop:
	@echo "Stopping development stack..."
	docker-compose -f infra/docker/compose.dev.yml down

# Database migrations
db-migrate:
	@echo "Running database migrations..."
	cd services/api && python -m alembic upgrade head

# Database seed
db-seed:
	@echo "Seeding database..."
	cd services/api && python -m scripts.seed

# Help
help:
	@echo "Available commands:"
	@echo "  all-checks    - Run all quality checks"
	@echo "  mcp-health    - Check MCP server health"
	@echo "  install       - Install all dependencies"
	@echo "  clean         - Clean build artifacts"
	@echo "  dev-setup     - Setup development environment"
	@echo "  prod-build    - Build for production"
	@echo "  docker-dev    - Start development stack"
	@echo "  docker-stop   - Stop development stack"
	@echo "  db-migrate    - Run database migrations"
	@echo "  db-seed       - Seed database"
	@echo "  help          - Show this help"
