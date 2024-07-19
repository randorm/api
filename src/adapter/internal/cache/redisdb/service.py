import pickle
from typing import TypeVar

import redis
import redis.asyncio
from pydantic import BaseModel
from redis.asyncio.client import Redis as AsyncRedis

import src.domain.model as domain
import src.protocol.internal.cache as proto

V = TypeVar("V", bound=BaseModel)


class RedisService(proto.CacheProtocol[V]):
    def __init__(self, redis_dsn: str):
        self._redis_dsn = redis_dsn
        self._client: AsyncRedis = redis.asyncio.from_url(self._redis_dsn)

    async def put(self, key: domain.ObjectID, value: V) -> None:
        await self._client.set(key.binary, pickle.dumps(value))

    async def get(self, key: domain.ObjectID) -> V | None:
        data = await self._client.get(key.binary)

        if data is not None:
            return pickle.loads(data)  # type: ignore

        return None

    async def delete(self, key: domain.ObjectID) -> None:
        await self._client.delete(key.binary)

    async def put_many(self, items: list[tuple[domain.ObjectID, V]]) -> None:
        values = {key.binary: pickle.dumps(value) for key, value in items}
        await self._client.mset(mapping=values)

    async def get_many(self, keys: list[domain.ObjectID]) -> list[V | None]:
        values = await self._client.mget(*[key.binary for key in keys])
        return [pickle.loads(v) if v is not None else None for v in values]

    async def delete_many(self, keys: list[domain.ObjectID]) -> None:
        values = [key.binary for key in keys]
        await self._client.delete(*values)

    async def flush(self) -> None:
        await self._client.flushdb()
