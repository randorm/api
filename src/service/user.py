import src.domain.model as domain
import src.protocol.internal.database.user as proto
from src.domain.exception.service import CreateUserException, ReadUserException


class UserService:
    def __init__(self, user_repository: proto.UserDatabaseProtocol):
        self.__user_repository = user_repository

    async def create_user(self, user: proto.CreateUser) -> domain.User:
        users = await self.__user_repository.find_users(
            proto.FindUsersByTid(tid=user.tid)
        )
        if len(users) > 0:
            raise CreateUserException("user already exists")

        try:
            return await self.__user_repository.create_user(user)
        except Exception as e:
            raise CreateUserException(
                f"failed to reflect user type with error: {e}"
            ) from e

    async def exists(self, user_tid: int) -> bool:
        users = await self.__user_repository.find_users(
            proto.FindUsersByTid(tid=user_tid)
        )
        return len(users) > 0

    async def find_user_by_tid(self, user_tid: int) -> domain.User:
        users = await self.__user_repository.find_users(
            proto.FindUsersByTid(tid=user_tid)
        )
        if len(users) > 0:
            return users[0]
        else:
            raise ReadUserException("user not found")

    async def read_user(self, user: proto.ReadUser) -> domain.User:
        return await self.__user_repository.read_user(user)

    async def update_user(self, user: proto.UpdateUser) -> domain.User:
        return await self.__user_repository.update_user(user)

    async def delete_user(self, user: proto.DeleteUser) -> domain.User:
        return await self.__user_repository.delete_user(user)