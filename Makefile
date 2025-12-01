.PHONY: help install run lint format test

help:
	@echo ''
	@echo 'Usage:'
	@echo '  make install    Install dependencies using Poetry'
	@echo '  make run        Run the application'
	@echo '  make lint       Lint code using ruff and black'
	@echo '  make format     Format code using black'
	@echo '  make test       Run tests with pytest'
	@echo '  make help       Show this help message'
	@echo ''

install:
	poetry install

run:
	poetry run python -m stash_app

lint:
	poetry run ruff stash_app
	poetry run black stash_app

format:
	poetry run black stash_app

test:
	poetry run pytest

.DEFAULT_GOAL := help
