default:
    just --list

setup:
    poetry install
    poetry run pre-commit install
    poetry run pre-commit run --all-files

tidy path=".":
    poetry run isort {{ path }}
    poetry run ruff format {{ path }}
    just --fmt --unstable

check:
    poetry run ruff check

test path="./src/tests":
    poetry run pytest {{ path }} --cov=./ --cov-report=html --cov-report=term-missing

run-server n_workers="1":
    poetry run gunicorn main:app --bind 0.0.0.0:8080 --workers {{ n_workers }} --worker-class aiohttp.GunicornWebWorker

docker-build:
    docker buildx build . -t randorm-api:latest

docker-run:
    docker run -p 8080:8080 --name randorm-api --rm --detach randorm-api:latest