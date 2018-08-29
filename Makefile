SRC := datatypes

validate:
	$(MAKE) lint && \
	$(MAKE) typecheck && \
	$(MAKE) test


lint:
	poetry run flake8


typecheck:
	poetry run mypy $(SRC)


test:
	poetry run pytest


clean:
	find . -type d | grep -P '(\.mypy_cache$$|__pycache__$$|\.pytest_cache$$)' | xargs rm -rf
