setup:
    poetry install
    poetry run pre-commit install
    poetry run pre-commit run --all-files

tidy:
    poetry run isort .
    poetry run black .

check:
    poetry run ruff check

test:
    poetry run pytest . --cov=./ --cov-report=html --cov-report=term-missing
