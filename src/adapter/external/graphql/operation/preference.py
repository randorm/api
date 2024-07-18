from __future__ import annotations

import strawberry as sb

import src.adapter.external.graphql.type.preference as graphql
import src.protocol.internal.database.preference as proto
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info
from src.adapter.external.graphql.tool.permission import DefaultPermissions

PreferenceKindInput = sb.input(graphql.PreferenceKindType)
PreferenceStatusInput = sb.input(graphql.PreferenceStatusType)


class PreferenceQuery:
    @sb.field(permission_classes=[DefaultPermissions])
    async def preference(
        root: PreferenceQuery, info: Info[PreferenceQuery], id: scalar.ObjectID
    ) -> graphql.PreferenceType:
        return await info.context.preference.loader.load(id)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_preference(
        root: PreferenceQuery,
        info: Info[PreferenceQuery],
        kind: PreferenceKindInput,  # type: ignore
        status: PreferenceStatusInput,  # type: ignore
        user_id: scalar.ObjectID,
        target_id: scalar.ObjectID,
    ) -> graphql.PreferenceType:
        request = proto.CreatePreference(
            kind=kind,
            status=status,
            user_id=user_id,
            target_id=target_id,
        )
        data = await info.context.preference.service.create(request)
        return graphql.PreferenceType.from_pydantic(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def update_preference(
        root: PreferenceQuery,
        info: Info[PreferenceQuery],
        id: scalar.ObjectID,
        kind: PreferenceKindInput | None,  # type: ignore
        status: PreferenceStatusInput | None,  # type: ignore
    ) -> graphql.PreferenceType:
        request = proto.UpdatePreference(
            _id=id,
            kind=kind,
            status=status,
        )
        data = await info.context.preference.service.update(request)
        info.context.preference.loader.clear(id)
        return graphql.PreferenceType.from_pydantic(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def delete_preference(
        root: PreferenceQuery,
        info: Info[PreferenceQuery],
        id: scalar.ObjectID,
    ) -> graphql.PreferenceType:
        request = proto.DeletePreference(_id=id)
        data = await info.context.preference.service.delete(request)
        info.context.preference.loader.clear(id)
        return graphql.PreferenceType.from_pydantic(data)
