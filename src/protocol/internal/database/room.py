from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field

from src.domain.model.room import Room
from src.domain.model.scalar.object_id import ObjectID
from src.domain.model.user import Gender
from src.protocol.internal.database.mixin import ExcludeFieldMixin


class CreateRoom(ExcludeFieldMixin, Room): ...


class ReadRoom(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateRoom(ExcludeFieldMixin, Room):
    id: ObjectID = Field(alias="_id")  # type: ignore
    # optional fields
    name: str | None = Field(default=None)
    capacity: int | None = Field(default=None)
    occupied: int | None = Field(default=None)
    gender_restriction: Gender | None = Field(default=None)
    editors_ids: set[ObjectID] | None = Field(default=None)
    # exclude
    creator_id: Literal[None] = None


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
