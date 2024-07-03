default:
    just --list

setup:
    poetry install
    poetry run pre-commit install
    poetry run pre-commit run --all-files

tidy path=".":
    poetry run isort {{ path }}
    poetry run black {{ path }}
    just --fmt --unstable

check:
    poetry run ruff check

test path="./src/tests":
    poetry run pytest {{ path }} --cov=./ --cov-report=html --cov-report=term-missing

run-server:
    poetry run python3 -m aiohttp.web -H localhost -P 8080 src.app.http.server:init