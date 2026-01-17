.PHONY: help install dev build test lint clean docker-up docker-down

help:
	@echo "Argus - Stock Screening Web Application"
	@echo ""
	@echo "Commands:"
	@echo "  install      Install all dependencies"
	@echo "  dev          Start development servers"
	@echo "  build        Build for production"
	@echo "  test         Run all tests"
	@echo "  lint         Run linters"
	@echo "  clean        Clean build artifacts"
	@echo "  docker-up    Start Docker containers"
	@echo "  docker-down  Stop Docker containers"

install:
	cd backend && python -m venv venv && . venv/bin/activate && pip install -r requirements-dev.txt
	cd frontend && npm install

dev-backend:
	cd backend && . venv/bin/activate && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

dev:
	@echo "Run 'make dev-backend' and 'make dev-frontend' in separate terminals"

build:
	cd frontend && npm run build

test:
	cd backend && . venv/bin/activate && pytest
	cd frontend && npm test

test-backend:
	cd backend && . venv/bin/activate && pytest -v

lint:
	cd backend && . venv/bin/activate && ruff check app/
	cd frontend && npm run lint

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +
	rm -rf backend/.coverage backend/htmlcov
	rm -rf frontend/dist frontend/coverage

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-logs:
	docker-compose logs -f
