.PHONY: check lint test

check: test

lint:
	flake8
	mypy src

test: lint
	pytest
