from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

from src.domain.model.user import User


class OAuthContainer(ABC):
    @classmethod
    @abstractmethod
    def construct(cls, data: Any) -> OAuthContainer: ...

    @abstractmethod
    def to_dto(self) -> BaseModel: ...


class OauthProtocol(ABC):
    @abstractmethod
    async def verify_callback_data(self, data: Any) -> OAuthContainer: ...

    @abstractmethod
    async def retrieve_user(self, data: OAuthContainer) -> User: ...
