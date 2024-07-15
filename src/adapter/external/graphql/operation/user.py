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


@sb.type
class UserQuery:
    @sb.field(permission_classes=[DefaultPermissions])
    async def user(
        root: UserQuery, info: Info[UserQuery], id: scalar.ObjectID
    ) -> UserType:  # type: ignore
        return await info.context.user.loader.load(id)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_user(
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
        return UserType.from_pydantic(data)

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
        return UserType.from_pydantic(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def delete_user(
        root: UserQuery, info: Info[UserQuery], id: scalar.ObjectID
    ) -> UserType:
        data = await info.context.user.service.delete(proto.DeleteUser(_id=id))
        info.context.user.loader.clear(id)  # invalidate cache
        return UserType.from_pydantic(data)
