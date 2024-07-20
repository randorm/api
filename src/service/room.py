import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.service import common
from src.service.base import BaseService
from src.utils.logger.logger import Logger

log = Logger("room-service")


class RoomService(BaseService):
    def __init__(
        self,
        room_repo: proto.RoomDatabaseProtocol,
        user_repo: proto.UserDatabaseProtocol,
    ):
        self._room_repo = room_repo
        self._user_repo = user_repo

    async def create(self, room: proto.CreateRoom) -> domain.Room:
        try:
            log.debug("creating new room")

            log.debug("checking room creator existence")
            if not await common.check_creator_exist(room, self._user_repo):
                log.error("creator does not exist")
                raise service_exception.CreateRoomException("creator does not exist")

            log.debug("checking room editors existence")
            if not await common.check_editors_exist(room, self._user_repo):
                log.error("one or more editors do not exist")
                raise service_exception.CreateRoomException(
                    "one or more editors do not exist"
                )

            log.debug("creating new room")
            return await self._room_repo.create_room(room)
        except service_exception.ServiceException as e:
            log.error("failed to create room with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to create room with error: {}", e)
            raise service_exception.CreateRoomException(
                "service failed to create room"
            ) from e

    async def read(self, room: proto.ReadRoom) -> domain.Room:
        try:
            log.debug(f"reading room {room.id}")
            return await self._room_repo.read_room(room)
        except Exception as e:
            log.error("failed to read room with error: {}", e)
            raise service_exception.ReadRoomException(
                "service failed to read room"
            ) from e

    async def update(self, room: proto.UpdateRoom) -> domain.Room:
        try:
            log.debug(f"updating room {room.id}")

            log.debug("checking room creator non-updateability")
            if room.creator_id is not None:
                log.error("can not change creator")
                raise service_exception.UpdateRoomException(
                    "creator can not be changed"
                )

            log.debug(f"updating room {room.id}")
            return await self._room_repo.update_room(room)
        except service_exception.ServiceException as e:
            log.error("failed to update room with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to update room with error: {}", e)
            raise service_exception.UpdateRoomException(
                "service failed to update room"
            ) from e

    async def delete(self, room: proto.DeleteRoom) -> domain.Room:
        try:
            log.debug(f"deleting room {room.id}")
            return await self._room_repo.delete_room(room)
        except Exception as e:
            log.error("failed to delete room with error: {}", e)
            raise service_exception.DeleteRoomException(
                "service failed to delete room"
            ) from e

    async def read_many(self, rooms: list[proto.ReadRoom]) -> list[domain.Room]:
        try:
            log.debug(f"reading rooms {[str(room.id) for  room in rooms]}")
            documents = await self._room_repo.read_many_rooms(rooms)
            results = []
            for request, response in zip(rooms, documents, strict=True):
                if response is None:
                    log.error(f"failed to read room {request.id}")
                    raise service_exception.ReadRoomException(
                        f"failed to read room {request.id}"
                    )

                results.append(response)
            log.info(f"read rooms {[str(room.id) for  room in rooms]}")
            return results
        except service_exception.ServiceException as e:
            log.error("failed to read rooms with error: {}", e)
            raise e
        except ValueError as e:  # raised by zip
            log.error("failed to read rooms with error: {}", e)
            raise service_exception.ReadRoomException("failed to read rooms") from e
        except Exception as e:
            log.error("failed to read rooms with error: {}", e)
            raise service_exception.ReadRoomException("failed to read rooms") from e
