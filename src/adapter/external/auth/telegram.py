from __future__ import annotations

import hashlib
import hmac
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ValidationError

from src.domain.exception import auth as auth_exception
from src.domain.exception import database as database_exception
from src.domain.exception import service as service_exception
from src.domain.model.scalar.object_id import ObjectID
from src.domain.model.user import Profile, User
from src.protocol.external.auth.oauth import OAuthContainer, OauthProtocol
from src.protocol.internal.database.user import (
    CreateUser,
    ReadUser,
)
from src.service.user.create import CreateUserService


class TelegramUserProfileMixin(Profile): ...


class TelegramAuthCallback(BaseModel):
    id: int
    auth_date: datetime
    first_name: str | None
    last_name: str | None
    username: str | None
    photo_url: str | None
    hash: str

    profile: TelegramUserProfileMixin

    __field_order__ = [
        "auth_date",
        "first_name",
        "id",
        "last_name",
        "photo_url",
        "username",
    ]

    def to_data_string(self) -> str:
        data_string = ""
        for field in self.__field_order__:
            data_string += f"{field}={getattr(self, field, "") or ""}\n"

        return data_string


class TelegramOauthContainer(BaseModel, OAuthContainer):
    id: ObjectID
    tid: int

    @classmethod
    def construct(cls, data: Any) -> TelegramOauthContainer:
        return TelegramOauthContainer.model_validate(data, from_attributes=True)

    def to_dto(self) -> TelegramOauthContainer:
        return self


class TelegramOauthAdapter(OauthProtocol):
    __secret_token: str
    __service: CreateUserService

    def __init__(self, secret_token: str, service: CreateUserService):
        self.__secret_token = secret_token
        self.__service = service

    async def verify_callback_data(self, data: Any) -> OAuthContainer:
        try:
            data = TelegramAuthCallback.model_validate(data, from_attributes=True)
        except ValidationError as e:
            raise auth_exception.InvalidCredentialsException(
                "failed to validate callback data"
            ) from e

        signing = hmac.new(
            self.__secret_token.encode(), data.to_data_string().encode(), hashlib.sha256
        )
        if signing.hexdigest() != data.hash:
            raise auth_exception.InvalidCredentialsException(
                "data is malformed since the hash does not match"
            )

        try:
            user = await self.__service.create_user(
                CreateUser(tid=data.id, profile=data.profile)
            )
        except (ValidationError, database_exception.ReflectUserException) as e:
            raise auth_exception.InvalidCredentialsException(
                "failed to reflect user data to create user"
            ) from e
        except service_exception.CreateUserException as e:
            raise auth_exception.UserAlreadyExistsException(
                "creating new user failed"
            ) from e

        return TelegramOauthContainer(id=user.id, tid=user.tid)

    async def retrieve_user(self, data: OAuthContainer) -> User:
        try:
            data = TelegramOauthContainer.model_validate(data.to_dto())

            user = await self.__service.read_user(ReadUser(_id=data.id))
        except (ValidationError, AttributeError) as e:
            raise auth_exception.InvalidCredentialsException("invalid data type") from e
        except database_exception.ReflectUserException as e:
            raise auth_exception.InvalidCredentialsException(
                "failed to reflect user data to create user"
            ) from e
        except database_exception.ReadUserException as e:
            raise auth_exception.UserNotFoundException("user not found") from e
        else:
            return user
