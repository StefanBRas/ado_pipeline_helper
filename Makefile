
.PHONY: format lint test
format:
	poetry run black src tests
	poetry run isort src tests

lint:
	poetry run ruff src tests

test:
	poetry run nox -r



