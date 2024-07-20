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

test path="./src/tests" n_workers="8":
    docker run -d -p 27017:27017 --rm --name randorm-api-tests-mongo mongodb/mongodb-community-server:latest
    poetry run pytest {{ path }} -n {{ n_workers }} --cov=./ --cov-report=html --cov-report=term-missing
    docker stop randorm-api-tests-mongo

run-server n_workers="1":
    poetry run gunicorn main:app --bind localhost:8080 --workers {{ n_workers }} --worker-class aiohttp.GunicornWebWorker

docker-build:
    docker buildx build . -t randorm-api:latest

docker-run:
    docker run -p 8080:8080 --name randorm-api --rm --detach randorm-api:latest