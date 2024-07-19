import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database.room as proto
from src.service.base import BaseService

# todo: define all business logic


class RoomService(BaseService):
    def __init__(self, repo: proto.RoomDatabaseProtocol):
        self._repo = repo

    async def create(self, room: proto.CreateRoom) -> domain.Room:
        try:
            return await self._repo.create_room(room)
        except Exception as e:
            raise service_exception.CreateRoomException(
                "service failed to create room"
            ) from e

    async def read(self, room: proto.ReadRoom) -> domain.Room:
        try:
            return await self._repo.read_room(room)
        except Exception as e:
            raise service_exception.ReadRoomException(
                "service failed to read room"
            ) from e

    async def update(self, room: proto.UpdateRoom) -> domain.Room:
        try:
            return await self._repo.update_room(room)
        except Exception as e:
            raise service_exception.UpdateRoomException(
                "service failed to update room"
            ) from e

    async def delete(self, room: proto.DeleteRoom) -> domain.Room:
        try:
            return await self._repo.delete_room(room)
        except Exception as e:
            raise service_exception.DeleteRoomException(
                "service failed to delete room"
            ) from e