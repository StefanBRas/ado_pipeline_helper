
.PHONY: format lint test
format:
	poetry run black src
	poetry run isort src

lint:
	poetry run ruff src

test:
	poetry run nox



