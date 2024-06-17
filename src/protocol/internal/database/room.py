import datetime
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, SkipJsonSchema

from src.domain.model.room import Room
from src.domain.model.scalar.object_id import ObjectID
from src.domain.model.user import Gender


class CreateRoom(Room):
    # excluded fields
    id: SkipJsonSchema[int | None] = Field(default=None, exclude=True)  # type: ignore
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


class ReadRoom(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateRoom(Room):
    # optional fields
    name: str | None = Field(default=None)
    capacity: int | None = Field(default=None)
    occupied: int | None = Field(default=None)
    gender_restriction: Gender | None = Field(default=None)
    editor_ids: set[ObjectID] | None = Field(default=None)
    # creator_id: ObjectID | None = Field(default=None)

    # excluded fields
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


class DeleteRoom(BaseModel):
    id: ObjectID = Field(alias="_id")


class RoomDatabaseProtocol(ABC):
    @abstractmethod
    async def create_room(self, room: CreateRoom) -> Room: ...

    @abstractmethod
    async def read_room(self, room: ReadRoom) -> Room: ...

    @abstractmethod
    async def update_room(self, room: UpdateRoom) -> Room: ...

    @abstractmethod
    async def delete_room(self, room: DeleteRoom) -> Room: ...
