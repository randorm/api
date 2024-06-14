setup:
    poetry install
    poetry run pre-commit install
    poetry run pre-commit run --all-files

tidy:
    poetry run isort .
    poetry run black .

check:
    poetry run ruff check
