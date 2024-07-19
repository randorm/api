from typing import TypeVar

from pydantic import BaseModel

from src.protocol.internal.cache.generic import CacheProtocol

V = TypeVar("V", bound=BaseModel)


class MemoryDBService(CacheProtocol[V]):
    def __init__(self):
        self._cache = {}

    async def put(self, key: str, value: V) -> None:
        self._cache[key] = value

    async def get(self, key: str) -> V | None:
        return self._cache.get(key)

    async def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    async def put_many(self, items: list[tuple[str, V]]) -> None:
        for key, value in items:
            self._cache[key] = value

    async def get_many(self, keys: list[str]) -> list[V | None]:
        return [self._cache.get(key) for key in keys]

    async def delete_many(self, keys: list[str]) -> None:
        for key in keys:
            if key in self._cache:
                del self._cache[key]

    async def flush(self) -> None:
        self._cache.clear()
