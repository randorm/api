from abc import ABC, abstractmethod

from src.domain.model.room import Room


class CreateRoom: ...


class ReadRoom: ...


class UpdateRoom: ...


class DeleteRoom: ...


class RoomDatabaseProtocol(ABC):
    @abstractmethod
    async def create_room(self, room: CreateRoom) -> Room: ...

    @abstractmethod
    async def read_room(self, room: ReadRoom) -> Room: ...

    @abstractmethod
    async def update_room(self, room: UpdateRoom) -> Room: ...

    @abstractmethod
    async def delete_room(self, room: DeleteRoom) -> Room: ...
