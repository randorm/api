![Repo Poster](./.github/poster.png)

Server-side of Randorm service, written in Python.

## Features
- 🍓 GraphQL API powered by [Strawberry GraphQL](https://github.com/strawberry-graphql/strawberry)
- 🤖 Telegram Bot powered by [aiogram ](https://github.com/aiogram/aiogram) 
- 🛢️ Redis cache powered by [redis-py ](https://github.com/redis/redis-py) 
- 🗃️ MongoDB database powered by [beanie](https://github.com/roman-right/beanie)
- 🦅 Core Models powered by [pydantic](https://github.com/pydantic/pydantic)
- 🧙‍♂️ Logging powered by [loguru](https://github.com/Delgan/loguru)

## Conventions
- [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- [black formatter](https://black.readthedocs.io/en/stable/)
- [ruff linter](https://github.com/charliermarsh/ruff)  
- [google format docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html)

## Dev Tools 
|Tool|Description|
|---|---|
|[black](https://black.readthedocs.io/en/stable/)|uncompromising formatter - source of truth for code style & format|
|[ruff](https://github.com/charliermarsh/ruff)|the fastest & most accurate python linter|
|[precommit-hooks](https://pre-commit.com/)|manages git hooks|
|[just](https://github.com/casey/just#recipe-parameters)|imporved version of make - task runner|

## Project Setup

1. Install [python 3.12](https://www.python.org/downloads/)
2. Install [poetry v1.8.2](https://python-poetry.org/docs/#installation)
3. Install [just](https://github.com/casey/just) ([installation guide](https://github.com/casey/just?tab=readme-ov-file#installation))
4. Create a virtual environment, install dependencies, preheat pre-commit hooks and more using:
```bash
just setup
```
5. Activate the virtual environment in current shell using:
```bash
poetry shell
```

## Development

### Formatting

To sort imports and format code run:
```basg
just tidy
```

### Linting

To lint code run:
```bash
just check
```


### Testing
```bash
just test
```

### Launch API
```bash
just run-server
```

### Docker
```bash
just docker-build
```

```bash
just docker-run
```