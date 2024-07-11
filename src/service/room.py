import src.domain.model as domain
import src.protocol.internal.database.room as proto
from src.service.base import BaseService


class RoomService(BaseService):
    def __init__(self, repo: proto.RoomDatabaseProtocol):
        self._repo = repo

    async def create(self, room: proto.CreateRoom) -> domain.Room:
        raise NotImplementedError()

    async def read(self, room: proto.ReadRoom) -> domain.Room:
        raise NotImplementedError()

    async def update(self, room: proto.UpdateRoom) -> domain.Room:
        raise NotImplementedError()

    async def delete(self, room: proto.DeleteRoom) -> domain.Room:
        raise NotImplementedError()
