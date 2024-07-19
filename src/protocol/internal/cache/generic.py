from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

import src.domain.model as domain

V = TypeVar("V", bound=BaseModel)


class CacheProtocol[V](ABC):
    @abstractmethod
    async def put(self, key: domain.ObjectID, value: V) -> None: ...

    @abstractmethod
    async def get(self, key: domain.ObjectID) -> V | None: ...

    @abstractmethod
    async def delete(self, key: domain.ObjectID) -> None: ...

    @abstractmethod
    async def put_many(self, items: list[tuple[domain.ObjectID, V]]) -> None: ...

    @abstractmethod
    async def get_many(self, keys: list[domain.ObjectID]) -> list[V | None]: ...

    @abstractmethod
    async def delete_many(self, keys: list[domain.ObjectID]) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...
