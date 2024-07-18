from __future__ import annotations

import strawberry as sb

import src.adapter.external.graphql.type.room as graphql
import src.protocol.internal.database.room as proto
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info


@sb.type
class RoomQuery:
    @sb.field
    async def room(
        root: RoomQuery, info: Info[RoomQuery], id: scalar.ObjectID
    ) -> graphql.RoomType:
        return await info.context.room.loader.load(id)

    @sb.mutation
    async def new_room(
        root: RoomQuery,
        info: Info[RoomQuery],
        name: str,
        capacity: int,
        occupied: int,
        gender_restriction: graphql.GenderType | None,
        creator_id: scalar.ObjectID,
        editors_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.RoomType:
        request = proto.CreateRoom(
            name=name,
            capacity=capacity,
            occupied=occupied,
            gender_restriction=gender_restriction,
            creator_id=creator_id,
            editors_ids=set(editors_ids) if editors_ids else set(),
        )
        data = await info.context.room.service.create(request)
        return graphql.RoomType.from_pydantic(data)

    @sb.mutation
    async def update_room(
        root: RoomQuery,
        info: Info[RoomQuery],
        id: scalar.ObjectID,
        name: str | None = None,
        capacity: int | None = None,
        occupied: int | None = None,
        gender_restriction: graphql.GenderType | None = None,
        editors_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.RoomType:
        request = proto.UpdateRoom(
            _id=id,
            name=name,
            capacity=capacity,
            occupied=occupied,
            gender_restriction=gender_restriction,
            editors_ids=set(editors_ids) if editors_ids else None,
        )
        data = await info.context.room.service.update(request)
        info.context.room.loader.clear(id)
        return graphql.RoomType.from_pydantic(data)

    @sb.mutation
    async def delete_room(
        root: RoomQuery,
        info: Info[RoomQuery],
        id: scalar.ObjectID,
    ) -> graphql.RoomType:
        request = proto.DeleteRoom(_id=id)
        data = await info.context.room.service.delete(request)
        info.context.room.loader.clear(id)
        return graphql.RoomType.from_pydantic(data)
