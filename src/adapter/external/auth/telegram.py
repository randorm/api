from __future__ import annotations

import hmac
from collections import OrderedDict
from datetime import datetime
from hashlib import sha256
from typing import Any
from urllib.parse import parse_qsl, urlencode

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
from src.utils.logger.logger import Logger

log = Logger("telegram-auth-adapter")


class TgUserProfileMixin(Profile): ...


class TgOauthLoginCallback(BaseModel):
    id: int
    auth_date: datetime
    first_name: str | None
    last_name: str | None
    username: str | None
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

    def to_telegram_ordered_dict(self) -> OrderedDict:
        data = OrderedDict(
            id=self.id,
            first_name=self.first_name,
            last_name=self.last_name,
            username=self.username,
            photo_url=self.photo_url,
            auth_date=self.auth_date,
            hash=self.hash,
        )
        return data


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

    def _validate_hash(self, data: Any) -> bool:
        init_data = sorted(parse_qsl(urlencode(data)))
        data_check_string = "\n".join(f"{k}={v}" for k, v in init_data if k != "hash")
        hash_ = data["hash"]

        secret_key = sha256(self.__secret_token.encode())

        calculated_hash = hmac.new(
            key=secret_key.digest(), msg=data_check_string.encode(), digestmod=sha256
        ).hexdigest()

        return calculated_hash == hash_

    async def register(self, data: Any) -> TgOauthContainer:
        try:
            log.debug("building callback data from custom data")
            request: TgOauthRegisterCallback = TgOauthRegisterCallback.model_validate(
                data, from_attributes=True
            )

            if not self._validate_hash(request.to_telegram_ordered_dict()):
                log.error(
                    "failed to parse callback data with exception: invalid aiogram hash check"
                )
                raise auth_exception.InvalidCredentialsException("invalid hash")

            log.debug(f"creating new user with telegram_id={request.id}")
            user = await self.__service.create(
                CreateUser(telegram_id=request.id, profile=request.profile)
            )
        except (ValidationError, database_exception.ReflectUserException) as e:
            log.error(
                "failed to build callback data or reflect user data to create user with exception: {}",
                e,
            )
            raise auth_exception.InvalidCredentialsException(
                "failed to reflect user data to create user"
            ) from e
        except service_exception.CreateUserException as e:
            log.error("creating new user failed with service exception: {}", e)
            raise auth_exception.UserAlreadyExistsException(
                "creating new user failed"
            ) from e
        except auth_exception.AuthException as e:
            log.error("authentiocation failed with auth exception: {}", e)
            raise e

        return TgOauthContainer.construct(
            TgOauthDTO(id=user.id, telegram_id=user.telegram_id), self.__jwt_secret
        )

    async def login(self, data: Any) -> TgOauthContainer:
        try:
            log.debug("checking callback data hash")
            try:
                if not self._validate_hash(data):
                    log.error(
                        "failed to parse callback data with exception: invalid aiogram hash check"
                    )
                    raise auth_exception.InvalidCredentialsException("invalid hash")

                log.debug("callback data hash is valid")

                webapp_data = dict(parse_qsl(urlencode(data)))
            except ValueError as e:
                log.error("failed to parse callback data with exception: {}", e)
                raise auth_exception.InvalidCredentialsException("invalid hash") from e

            log.debug("building callback data from custom data")
            request = TgOauthLoginCallback.model_validate(webapp_data)

            log.debug("searching user by telegram id")
            user = await self.__service.find_by_telegram_id(request.id)
        except auth_exception.AuthException as e:
            raise e
        except service_exception.ReadUserException as e:
            log.error("reading user failed with service exception: {}", e)
            raise auth_exception.UserNotFoundException("reading user failed") from e
        except ValidationError as e:
            log.error(
                "failed to build callback data or reflect user data to read user with exception: {}",
                e,
            )
            raise auth_exception.InvalidCredentialsException(
                "failed to reflect user data to read user"
            ) from e
        except Exception as e:
            log.error("authentiocation failed with auth exception: {}", e)
            raise e

        return TgOauthContainer.construct(
            TgOauthDTO(id=user.id, telegram_id=user.telegram_id), self.__jwt_secret
        )

    async def retrieve_user(self, data: TgOauthContainer) -> User:
        try:
            if not isinstance(data, TgOauthContainer):
                log.error(
                    "invalid data type was passed to retrieve user function. "
                    f"expected TgOauthContainer, got {type(data)}"
                )
                raise auth_exception.InvalidCredentialsException("invalid data type")

            try:
                log.debug("building dto from container")
                dto = data.to_dto(self.__jwt_secret)
            except Exception as e:
                log.error("failed to build dto from container with exception: {}", e)
                raise auth_exception.InvalidCredentialsException(
                    "invalid data type"
                ) from e

            user = await self.__service.read(ReadUser(_id=dto.id))
        except (ValidationError, AttributeError) as e:
            log.error(
                "failed to construct dto or reflect to read user with exception: {}", e
            )
            raise auth_exception.InvalidCredentialsException("invalid data type") from e
        except service_exception.ReadUserException as e:
            log.error("reading user failed with service exception: {}", e)
            raise auth_exception.UserNotFoundException("user not found") from e
        else:
            log.debug(
                f"user id={user.id}, telegram_id={user.telegram_id} was retrieved",
            )
            return user
