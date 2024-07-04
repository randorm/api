import datetime
from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field

from src.domain.model.scalar.object_id import ObjectID
from src.domain.model.user import Gender, LanguageCode, Profile, User
from src.protocol.internal.database.mixin import ExcludeFieldMixin

# todo: pydantic v2 has no ability to generate DTO types
# todo: tracking issue https://github.com/pydantic/pydantic/issues/9573


class CreateUser(ExcludeFieldMixin, User): ...


class FindUsersByTid(BaseModel):
    telegram_id: int


class FindUsersByProfileUsername(BaseModel):
    username: str


type FindUsers = FindUsersByTid | FindUsersByProfileUsername


class ReadUser(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateProfile(Profile):
    # optional fields
    first_name: str | None = Field(default=None)
    last_name: str | None = Field(default=None)
    username: str | None = Field(default=None)
    language_code: LanguageCode | None = Field(default=None)
    gender: Gender | None = Field(default=None)
    birthdate: datetime.date | None = Field(default=None)


class UpdateUser(ExcludeFieldMixin, User):
    id: ObjectID = Field(alias="_id")
    # optional fields
    views: int | None = Field(default=None)
    profile: UpdateProfile | None = Field(default=None)
    # exclude
    telegram_id: Literal[None] = None


class DeleteUser(BaseModel):
    id: ObjectID = Field(alias="_id")


class UserDatabaseProtocol(ABC):
    @abstractmethod
    async def create_user(self, user: CreateUser) -> User: ...

    @abstractmethod
    async def find_users(self, user: FindUsers) -> list[User]: ...

    @abstractmethod
    async def read_user(self, user: ReadUser) -> User: ...

    @abstractmethod
    async def update_user(self, user: UpdateUser) -> User: ...

    @abstractmethod
    async def delete_user(self, user: DeleteUser) -> User: ...
