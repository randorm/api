import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database.user as proto
from src.domain.exception.database import DeleteUserException
from src.service.base import BaseService
from src.utils.logger.logger import Logger

log = Logger("user-service")


class UserService(BaseService):
    def __init__(self, repo: proto.UserDatabaseProtocol):
        self.__repo = repo

    async def create(self, user: proto.CreateUser) -> domain.User:
        try:
            log.debug("creating new user")

            log.debug("checking user existence")
            users = await self.__repo.find_users(
                proto.FindUsersByTid(telegram_id=user.telegram_id)
            )
            log.info(f"found users {[user.telegram_id for user in users]}")
            if len(users) > 0:
                log.error("user already exists")
                raise service_exception.CreateUserException("user already exists")

                log.debug("creating new user")
            return await self.__repo.create_user(user)
        except Exception as e:
            log.error("failed to create user with error: {}", e)
            raise service_exception.CreateUserException(
                "service failed to create user"
            ) from e

    async def exists(self, user_telegram_id: int) -> bool:
        try:
            log.debug(f"checking user existence with telegram id {user_telegram_id}")
            users = await self.__repo.find_users(
                proto.FindUsersByTid(telegram_id=user_telegram_id)
            )
            log.info(f"found users {[user.telegram_id for user in users]}")
            return len(users) > 0
        except Exception as e:
            log.error("failed to check user existence with error: {}", e)
            raise service_exception.ReadUserException(
                "service failed to read user"
            ) from e

    async def find_by_telegram_id(self, user_tid: int) -> domain.User:
        try:
            log.debug(f"finding user with telegram id {user_tid}")
            users = await self.__repo.find_users(
                proto.FindUsersByTid(telegram_id=user_tid)
            )
            log.info(f"found users {[user.telegram_id for user in users]}")
            if len(users) != 0:
                return users[0]
            else:
                log.error("neither or too many users found")
                raise service_exception.ReadUserException("service failed to find user")
        except service_exception.ServiceException as e:
            log.error("failed to find user with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to find user with error: {}", e)
            raise service_exception.ReadUserException(
                "service failed to find user"
            ) from e

    async def read(self, user: proto.ReadUser) -> domain.User:
        try:
            log.debug(f"reading user {user.id}")
            return await self.__repo.read_user(user)
        except Exception as e:
            log.error("failed to read user with error: {}", e)
            raise service_exception.ReadUserException(
                "service failed to read user"
            ) from e

    async def update(self, user: proto.UpdateUser) -> domain.User:
        try:
            log.debug(f"updating user {user.id}")

            log.debug("checking user telegram id non-updateability")
            if user.telegram_id is not None:
                log.error("can not change telegram id")
                raise service_exception.UpdateUserException(
                    "telegram_id can not be changed"
                )

            log.debug(f"updating user {user.id}")
            return await self.__repo.update_user(user)
        except service_exception.ServiceException as e:
            log.error("failed to update user with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to update user with error: {}", e)
            raise service_exception.UpdateUserException(
                "service failed to update user"
            ) from e

    async def delete(self, user: proto.DeleteUser) -> domain.User:
        try:
            log.debug(f"deleting user {user.id}")
            return await self.__repo.delete_user(user)
        except Exception as e:
            log.error("failed to delete user with error: {}", e)
            raise DeleteUserException("service failed to delete user") from e

    async def read_many(self, users: list[proto.ReadUser]) -> list[domain.User]:
        try:
            log.debug(f"reading users {[str(user.id) for  user in users]}")
            documents = await self.__repo.read_many_users(users)
            results = []
            for request, response in zip(users, documents, strict=True):
                if response is None:
                    log.error(f"failed to read user {request.id}")
                    raise service_exception.ReadUserException(
                        f"failed to read user {request.id}"
                    )

                results.append(response)
            log.info(f"read users {[str(user.id) for  user in users]}")
            return results
        except service_exception.ServiceException as e:
            log.error("failed to read users with error: {}", e)
            raise e
        except ValueError as e:  # raised by zip
            log.error("failed to read users with error: {}", e)
            raise service_exception.ReadUserException("failed to read users") from e
        except Exception as e:
            log.error("failed to read users with error: {}", e)
            raise service_exception.ReadUserException("failed to read users") from e
