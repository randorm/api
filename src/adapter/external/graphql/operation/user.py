from __future__ import annotations

from datetime import datetime

import strawberry as sb

import src.protocol.internal.database.user as proto
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info
from src.adapter.external.graphql.tool.permission import DefaultPermissions
from src.adapter.external.graphql.type.user import (
    GenderType,
    LanguageCodeType,
    UserType,
)
from src.utils.logger.logger import Logger

log = Logger("graphql-user-ops")


@sb.type
class UserQuery:
    @sb.field(permission_classes=[DefaultPermissions])
    async def user(
        root: UserQuery, info: Info[UserQuery], id: scalar.ObjectID
    ) -> UserType:
        with log.activity(f"loading user {id}"):
            return await info.context.user.loader.load(id)

    @sb.field(permission_classes=[DefaultPermissions])
    async def me(root: UserQuery, info: Info[UserQuery]) -> UserType:
        with log.activity("loading user"):
            if info.context.user_id is None:
                raise Exception("User is not authenticated")
            return await info.context.user.loader.load(info.context.user_id)


@sb.type
class UserMutation:
    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_user(
        root: UserMutation,
        info: Info[UserMutation],
        telegram_id: scalar.BigInt,
        first_name: str,
        language_code: LanguageCodeType,  # type: ignore
        gender: GenderType,  # type: ignore
        birthdate: datetime,
        last_name: str | None = None,
        username: str | None = None,
        views: int = 0,
    ) -> UserType:
        with log.activity("creating new user"):
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
            log.info(f"created user {data.id}")
            return UserType.from_pydantic(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def update_user(
        root: UserMutation,
        info: Info[UserMutation],
        id: scalar.ObjectID,
        views: int | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        username: str | None = None,
        language_code: LanguageCodeType | None = None,  # type: ignore
        gender: GenderType | None = None,  # type: ignore
        birthdate: datetime | None = None,
    ) -> UserType:
        with log.activity(f"updating user {id}"):
            payload = proto.UpdateUser(
                _id=id,
                views=views,
                profile=proto.UpdateProfile(
                    first_name=first_name,
                    last_name=last_name,
                    username=username,
                    language_code=language_code,
                    gender=gender,
                    birthdate=birthdate,
                ),
            )

            request = proto.UpdateUser.model_validate(payload)
            data = await info.context.user.service.update(request)
            info.context.user.loader.clear(request.id)  # invalidate old cache
            log.info(f"updated user {id}")
            return UserType.from_pydantic(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def delete_user(
        root: UserMutation, info: Info[UserMutation], id: scalar.ObjectID
    ) -> UserType:
        with log.activity(f"deleting user {id}"):
            data = await info.context.user.service.delete(proto.DeleteUser(_id=id))
            info.context.user.loader.clear(id)  # invalidate cache
            log.info(f"deleted user {id}")
            return UserType.from_pydantic(data)
