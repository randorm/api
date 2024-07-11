from __future__ import annotations

from datetime import datetime

import strawberry as sb
from pydantic import ValidationError

import src.domain.exception as exception
import src.protocol.internal.database.user as proto
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info
from src.adapter.external.graphql.tool.permission import DefaultPermissions
from src.adapter.external.graphql.type.user import (
    GenderType,
    LanguageCodeType,
    UserType,
)


@sb.type
class UserQuery:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @sb.field(permission_classes=[DefaultPermissions])
    async def user(
        root: UserQuery, info: Info[UserQuery], id: scalar.ObjectID
    ) -> UserType:
        try:
            return await info.context.user.loader.load(id)
        except (
            exception.database.ReadUserException,
            exception.service.ReadUserException,
        ) as e:
            raise ValueError(f"user with id {id} does not exist") from e
        except exception.service.ServiceException as e:
            raise ValueError("conflicted data") from e
        except exception.database.DatabaseException as e:
            raise ValueError("database error") from e
        except Exception as e:
            raise ValueError("unknown error") from e

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def create_user(
        root: UserQuery,
        info: Info[UserQuery],
        telegram_id: int,
        first_name: str,
        language_code: LanguageCodeType,  # type: ignore
        gender: GenderType,  # type: ignore
        birthdate: datetime,
        last_name: str | None = None,
        username: str | None = None,
        views: int = 0,
    ) -> UserType:
        try:
            failed = True

            request = proto.CreateUser(
                telegram_id=telegram_id,
                profile=proto.Profile(
                    first_name=first_name,
                    language_code=language_code,
                    gender=gender,
                    birthdate=birthdate,
                    last_name=last_name,
                    username=username,
                ),
                views=views,
            )
            data = await info.context.user.service.create(request)
            response = await info.context.user.loader.load(data.id)  # cache
        except ValidationError as e:
            raise ValueError("invalid data") from e
        except (
            exception.database.CreateUserException,
            exception.service.CreateUserException,
        ) as e:
            raise ValueError("user already exists") from e
        except exception.service.ServiceException as e:
            raise ValueError("conflicted data") from e
        except exception.database.DatabaseException as e:
            raise ValueError("database error") from e
        except Exception as e:
            raise ValueError("unknown error") from e
        else:
            failed = False
            return response
        finally:
            if failed:
                ...

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def update_user(
        root: UserQuery,
        info: Info[UserQuery],
        id: scalar.ObjectID,
        views: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
        language_code: LanguageCodeType | None = None,  # type: ignore
        gender: GenderType | None = None,  # type: ignore
        birthdate: datetime | None = None,
    ) -> UserType:
        try:
            failed = True

            payload = {
                "id": id,
                "profile": {
                    "first_name": first_name,
                    "last_name": last_name,
                    "username": username,
                    "language_code": language_code,
                    "gender": gender,
                    "birthdate": birthdate,
                },
                "views": views,
            }

            request = proto.UpdateUser.model_validate(payload)
            data = await info.context.user.service.update(request)
            info.context.user.loader.clear(request.id)  # invalidate cache
            response = UserType(**data.model_dump(mode="json", by_alias=False))
        except ValidationError as e:
            raise ValueError("invalid data") from e
        except (
            exception.database.UpdateUserException,
            exception.service.UpdateUserException,
        ) as e:
            raise ValueError(f"user with id {id} does not exist") from e
        except exception.service.ServiceException as e:
            raise ValueError("conflicted data") from e
        except exception.database.DatabaseException as e:
            raise ValueError("database error") from e
        except Exception as e:
            raise ValueError("unknown error") from e
        else:
            failed = False
            return response
        finally:
            if failed:
                info.context.user.loader.clear(request.id)  # invalidate cache

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def delete_user(
        root: UserQuery, info: Info[UserQuery], id: scalar.ObjectID
    ) -> UserType:
        try:
            failed = True
            data = await info.context.user.service.delete(proto.DeleteUser(_id=id))
            info.context.user.loader.clear(id)  # invalidate cache
            response = UserType.from_pydantic(data)
        except (
            exception.database.DeleteUserException,
            exception.service.DeleteUserException,
        ) as e:
            raise ValueError(f"user with id {id} does not exist") from e
        except exception.service.ServiceException as e:
            raise ValueError("conflicted data") from e
        except exception.database.DatabaseException as e:
            raise ValueError("database error") from e
        except Exception as e:
            raise ValueError("unknown error") from e
        else:
            failed = False
            return response
        finally:
            if failed:
                info.context.user.loader.clear(id)  # invalidate cache
