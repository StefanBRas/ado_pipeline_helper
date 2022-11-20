
.PHONY: lint
format:
	poetry run black src
	poetry run isort src

lint:
	poetry run ruff src



