import pickle
from typing import TypeVar

import redis
import redis.asyncio
from pydantic import BaseModel

import src.domain.model as domain
import src.protocol.internal.cache as proto

V = TypeVar("V", bound=BaseModel)


class RedisService(proto.CacheProtocol[V]):
    def __init__(self, redis_dsn: str):
        self._redis_dsn = redis_dsn
        self._client = redis.from_url(self._redis_dsn)

    def put(self, key: domain.ObjectID, value: V) -> None:
        self._client.set(key.binary, pickle.dumps(value))

    def get(self, key: domain.ObjectID) -> V | None:
        data = self._client.get(key.binary)

        if data is not None:
            return pickle.loads(data)  # type: ignore

        return None

    def delete(self, key: domain.ObjectID) -> None:
        self._client.delete(key.binary)

    def put_many(self, items: list[tuple[domain.ObjectID, V]]) -> None:
        self._client.mset({key.binary: pickle.dumps(value) for key, value in items})

    def get_many(self, keys: list[domain.ObjectID]) -> list[V | None]:
        return [
            pickle.loads(v) for v in self._client.mget(*[key.binary for key in keys])  # type: ignore
        ]

    def delete_many(self, keys: list[domain.ObjectID]) -> None:
        self._client.delete(*[key.binary for key in keys])

    def flush(self) -> None:
        self._client.flushdb()
