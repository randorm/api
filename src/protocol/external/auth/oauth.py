from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from src.domain.model.user import User


class OAuthDTO(BaseModel): ...


class OAuthContainer(ABC):
    @classmethod
    @abstractmethod
    def construct(cls, data: Any, *args, **kwargs) -> OAuthContainer: ...

    @abstractmethod
    def to_dto(self, *args, **kwargs) -> BaseModel: ...


class OauthProtocol(ABC):
    @abstractmethod
    async def register(self, data: Any) -> OAuthContainer: ...

    @abstractmethod
    async def login(self, data: Any) -> OAuthContainer: ...

    @abstractmethod
    async def retrieve_user(self, data: OAuthContainer) -> User: ...
