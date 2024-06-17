from abc import ABC, abstractmethod

from src.domain.model.user import User


class CreateUser: ...


class ReadUser: ...


class UpdateUser: ...


class DeleteUser: ...


class UserDatabaseProtocol(ABC):
    @abstractmethod
    async def create_user(self, user: CreateUser) -> User: ...

    @abstractmethod
    async def read_user(self, user: ReadUser) -> User: ...

    @abstractmethod
    async def update_user(self, user: UpdateUser) -> User: ...

    @abstractmethod
    async def delete_user(self, user: DeleteUser) -> User: ...
