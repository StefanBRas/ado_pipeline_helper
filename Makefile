RUN=poetry run

.PHONY: format lint test
format:
	poetry run black src tests

lint:
	${RUN} ruff src tests

test:
	poetry run nox -r



