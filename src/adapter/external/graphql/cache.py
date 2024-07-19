import asyncio
from typing import TypeVar

from pydantic import BaseModel
from strawberry.dataloader import AbstractCache

import src.domain.model as domain
from src.protocol.internal.cache.generic import CacheProtocol

T = TypeVar("T", bound=BaseModel)


class CacheMap[T](AbstractCache[domain.ObjectID, T]):
    def __init__(self, cache_service: CacheProtocol[T]):
        self._cache_service = cache_service

    def get(self, key: domain.ObjectID) -> asyncio.Future[T] | None:
        data = self._cache_service.get(key)
        if data is None:
            return data

        async def promise():
            return data

        return asyncio.ensure_future(promise())

    def set(self, key: domain.ObjectID, value: asyncio.Future[T]) -> None:
        # Strawberry Cache Map is very bad
        # Wait until fixes, or implement own dataloader
        return self._cache_service.put(key, value)  # todo: fix

    def delete(self, key: domain.ObjectID) -> None:
        return self._cache_service.delete(key)

    def clear(self) -> None:
        return self._cache_service.flush()
