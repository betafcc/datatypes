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
