import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database.user as proto
from src.domain.exception.database import DeleteUserException
from src.service.base import BaseService

# todo: define all business logic


class UserService(BaseService):
    def __init__(self, user_repository: proto.UserDatabaseProtocol):
        self.__user_repository = user_repository

    async def create(self, user: proto.CreateUser) -> domain.User:
        users = await self.__user_repository.find_users(
            proto.FindUsersByTid(telegram_id=user.telegram_id)
        )
        if len(users) > 0:
            raise service_exception.CreateUserException("user already exists")

        try:
            return await self.__user_repository.create_user(user)
        except Exception as e:
            raise service_exception.CreateUserException(
                "service failed to create user"
            ) from e

    async def exists(self, user_tid: int) -> bool:
        try:
            users = await self.__user_repository.find_users(
                proto.FindUsersByTid(telegram_id=user_tid)
            )
            return len(users) > 0
        except Exception as e:
            raise service_exception.ReadUserException(
                "service failed to read user"
            ) from e

    async def find_by_telegram_id(self, user_tid: int) -> domain.User:
        try:
            users = await self.__user_repository.find_users(
                proto.FindUsersByTid(telegram_id=user_tid)
            )
            if len(users) > 0:
                return users[0]
            else:
                raise service_exception.ReadUserException("service failed to find user")
        except service_exception.ReadUserException as e:
            raise e
        except Exception as e:
            raise service_exception.ReadUserException(
                "service failed to find user"
            ) from e

    async def read(self, user: proto.ReadUser) -> domain.User:
        try:
            return await self.__user_repository.read_user(user)
        except Exception as e:
            raise service_exception.ReadUserException(
                "service failed to read user"
            ) from e

    async def update(self, user: proto.UpdateUser) -> domain.User:
        try:
            return await self.__user_repository.update_user(user)
        except Exception as e:
            raise service_exception.UpdateUserException(
                "service failed to update user"
            ) from e

    async def delete(self, user: proto.DeleteUser) -> domain.User:
        try:
            return await self.__user_repository.delete_user(user)
        except Exception as e:
            raise DeleteUserException("service failed to delete user") from e
