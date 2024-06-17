import datetime
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field
from pydantic.config import SkipJsonSchema

from src.domain.model.scalar.object_id import ObjectID
from src.domain.model.user import Gender, LanguageCode, Profile, User

# todo: pydantic v2 has no ability to generate DTO types
# todo: tracking issue https://github.com/pydantic/pydantic/issues/9573


class CreateUser(User):
    # excluded fields
    id: SkipJsonSchema[int | None] = Field(default=None, exclude=True)  # type: ignore
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


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


class UpdateUser(User):
    # optional fields
    views: int | None = Field(default=None)
    profile: UpdateProfile | None = Field(default=None)

    # excluded fields
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


class DeleteUser(BaseModel):
    id: ObjectID = Field(alias="_id")


class UserDatabaseProtocol(ABC):
    @abstractmethod
    async def create_user(self, user: CreateUser) -> User: ...

    @abstractmethod
    async def read_user(self, user: ReadUser) -> User: ...

    @abstractmethod
    async def update_user(self, user: UpdateUser) -> User: ...

    @abstractmethod
    async def delete_user(self, user: DeleteUser) -> User: ...
