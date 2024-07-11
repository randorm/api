from __future__ import annotations

import hashlib
import hmac
from datetime import datetime
from typing import Any

import jwt
from pydantic import BaseModel, ValidationError

from src.domain.exception import auth as auth_exception
from src.domain.exception import database as database_exception
from src.domain.exception import service as service_exception
from src.domain.model.scalar.object_id import ObjectID
from src.domain.model.user import Profile, User
from src.protocol.external.auth.oauth import OAuthContainer, OAuthDTO, OauthProtocol
from src.protocol.internal.database.user import CreateUser, ReadUser
from src.service.user import UserService


class TgUserProfileMixin(Profile): ...


class TgOauthLoginCallback(BaseModel):
    id: int
    auth_date: datetime
    first_name: str | None
    last_name: str | None
    username: str
    photo_url: str | None
    hash: str

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


class TgOauthRegisterCallback(TgOauthLoginCallback):
    profile: TgUserProfileMixin


class TgOauthDTO(OAuthDTO):
    id: ObjectID
    telegram_id: int


class TgOauthContainer(BaseModel, OAuthContainer):
    jwt: str

    @classmethod
    def construct(
        cls, data: TgOauthDTO, secret: str, *args, **kwargs
    ) -> TgOauthContainer:
        token = jwt.encode(data.model_dump(mode="json"), secret, algorithm="HS256")
        self = cls(jwt=token)
        return self

    def to_dto(self, secret: str, *args, **kwargs) -> TgOauthDTO:
        return TgOauthDTO.model_validate(
            jwt.decode(self.jwt, secret, algorithms=["HS256"])
        )

    def to_string(self, *args, **kwargs) -> str:
        return self.jwt


class TelegramOauthAdapter(OauthProtocol):
    __secret_token: str
    __jwt_secret: str
    __service: UserService

    def __init__(self, secret_token: str, jwt_secret: str, service: UserService):
        self.__secret_token = secret_token
        self.__jwt_secret = jwt_secret
        self.__service = service

    def __check_hash(
        self, data: TgOauthRegisterCallback | TgOauthLoginCallback
    ) -> None:
        signing = hmac.new(
            self.__secret_token.encode(),
            data.to_data_string().encode(),
            hashlib.sha256,
        )
        if signing.hexdigest() != data.hash:
            raise auth_exception.InvalidCredentialsException(
                "data is malformed since the hash does not match"
            )

    async def register(self, data: Any) -> TgOauthContainer:
        try:
            request: TgOauthRegisterCallback = TgOauthRegisterCallback.model_validate(
                data, from_attributes=True
            )
            self.__check_hash(request)

            user = await self.__service.create(
                CreateUser(telegram_id=request.id, profile=request.profile)
            )
        except (ValidationError, database_exception.ReflectUserException) as e:
            raise auth_exception.InvalidCredentialsException(
                "failed to reflect user data to create user"
            ) from e
        except service_exception.CreateUserException as e:
            raise auth_exception.UserAlreadyExistsException(
                "creating new user failed"
            ) from e
        except auth_exception.AuthException as e:
            raise e

        return TgOauthContainer.construct(
            TgOauthDTO(id=user.id, telegram_id=user.telegram_id), self.__jwt_secret
        )

    async def login(self, data: Any) -> TgOauthContainer:
        try:
            request = TgOauthLoginCallback.model_validate(data, from_attributes=True)
            self.__check_hash(request)

            user = await self.__service.find_by_telegram_id(request.id)
        except (ValidationError, database_exception.ReflectUserException) as e:
            raise auth_exception.InvalidCredentialsException(
                "failed to reflect user data to read user"
            ) from e
        except service_exception.ReadUserException as e:
            raise auth_exception.UserNotFoundException("reading user failed") from e
        except auth_exception.AuthException as e:
            raise e

        return TgOauthContainer.construct(
            TgOauthDTO(id=user.id, telegram_id=user.telegram_id), self.__jwt_secret
        )

    async def retrieve_user(self, data: TgOauthContainer) -> User:
        try:
            if not isinstance(data, TgOauthContainer):
                raise auth_exception.InvalidCredentialsException("invalid data type")

            try:
                dto = data.to_dto(self.__jwt_secret)
            except Exception as e:
                raise auth_exception.InvalidCredentialsException(
                    "invalid data type"
                ) from e

            user = await self.__service.read(ReadUser(_id=dto.id))
        except (ValidationError, AttributeError) as e:
            raise auth_exception.InvalidCredentialsException("invalid data type") from e
        except service_exception.ReadUserException as e:
            raise auth_exception.UserNotFoundException("user not found") from e
        else:
            return user
