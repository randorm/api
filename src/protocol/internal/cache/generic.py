from abc import ABC, abstractmethod
from typing import TypeVar

from pydantic import BaseModel

import src.domain.model as domain

V = TypeVar("V", bound=BaseModel)


class CacheProtocol[V](ABC):
    @abstractmethod
    def put(self, key: domain.ObjectID, value: V) -> None: ...

    @abstractmethod
    def get(self, key: domain.ObjectID) -> V | None: ...

    @abstractmethod
    def delete(self, key: domain.ObjectID) -> None: ...

    @abstractmethod
    def put_many(self, items: list[tuple[domain.ObjectID, V]]) -> None: ...

    @abstractmethod
    def get_many(self, keys: list[domain.ObjectID]) -> list[V | None]: ...

    @abstractmethod
    def delete_many(self, keys: list[domain.ObjectID]) -> None: ...

    @abstractmethod
    def flush(self) -> None: ...
