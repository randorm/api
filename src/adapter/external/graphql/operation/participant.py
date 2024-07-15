from __future__ import annotations

import strawberry as sb

import src.adapter.external.graphql.type.participant as graphql
import src.protocol.internal.database.participant as proto
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info
from src.adapter.external.graphql.tool.permission import DefaultPermissions


@sb.type
class ParticipantQuery:
    @sb.field(permission_classes=[DefaultPermissions])
    async def participant(
        root: ParticipantQuery, info: Info[ParticipantQuery], id: scalar.ObjectID
    ) -> graphql.ParticipantType:  # type: ignore
        return await info.context.participant.loader.load(id)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_creating_participant(
        root: ParticipantQuery,
        info: Info[ParticipantQuery],
        allocation_id: scalar.ObjectID,
        user_id: scalar.ObjectID,
        viewed_ids: list[scalar.ObjectID] | None = None,
        subscription_ids: list[scalar.ObjectID] | None = None,
        subscribers_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.CreatingParticipantType:
        request = proto.CreateCreatingParticipant(
            allocation_id=allocation_id,
            user_id=user_id,
            viewed_ids=set(viewed_ids) if viewed_ids else set(),
            subscription_ids=set(subscription_ids) if subscription_ids else set(),
            subscribers_ids=set(subscribers_ids) if subscribers_ids else set(),
        )
        data = await info.context.participant.service.create(request)
        return graphql.domain_to_participant(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_created_participant(
        root: ParticipantQuery,
        info: Info[ParticipantQuery],
        allocation_id: scalar.ObjectID,
        user_id: scalar.ObjectID,
        viewed_ids: list[scalar.ObjectID] | None = None,
        subscription_ids: list[scalar.ObjectID] | None = None,
        subscribers_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.CreatedParticipantType:
        request = proto.CreateCreatedParticipant(
            allocation_id=allocation_id,
            user_id=user_id,
            viewed_ids=set(viewed_ids) if viewed_ids else set(),
            subscription_ids=set(subscription_ids) if subscription_ids else set(),
            subscribers_ids=set(subscribers_ids) if subscribers_ids else set(),
        )
        data = await info.context.participant.service.create(request)
        return graphql.domain_to_participant(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_active_participant(
        root: ParticipantQuery,
        info: Info[ParticipantQuery],
        allocation_id: scalar.ObjectID,
        user_id: scalar.ObjectID,
        viewed_ids: list[scalar.ObjectID] | None = None,
        subscription_ids: list[scalar.ObjectID] | None = None,
        subscribers_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.ActiveParticipantType:
        request = proto.CreateActiveParticipant(
            allocation_id=allocation_id,
            user_id=user_id,
            viewed_ids=set(viewed_ids) if viewed_ids else set(),
            subscription_ids=set(subscription_ids) if subscription_ids else set(),
            subscribers_ids=set(subscribers_ids) if subscribers_ids else set(),
        )
        data = await info.context.participant.service.create(request)
        return graphql.domain_to_participant(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_allocated_participant(
        root: ParticipantQuery,
        info: Info[ParticipantQuery],
        user_id: scalar.ObjectID,
        allocation_id: scalar.ObjectID,
        room_id: scalar.ObjectID,
        viewed_ids: list[scalar.ObjectID] | None = None,
        subscription_ids: list[scalar.ObjectID] | None = None,
        subscribers_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.AllocatedParticipantType:
        request = proto.CreateAllocatedParticipant(
            allocation_id=allocation_id,
            user_id=user_id,
            viewed_ids=set(viewed_ids) if viewed_ids else set(),
            subscription_ids=set(subscription_ids) if subscription_ids else set(),
            subscribers_ids=set(subscribers_ids) if subscribers_ids else set(),
            room_id=room_id,
        )
        data = await info.context.participant.service.create(request)
        return graphql.domain_to_participant(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def update_participant(
        root: ParticipantQuery,
        info: Info[ParticipantQuery],
        id: scalar.ObjectID,
        room_id: scalar.ObjectID | None = None,
        state: graphql.ParticipantStateType | None = None,  # type: ignore
        viewed_ids: list[scalar.ObjectID] | None = None,
        subscription_ids: list[scalar.ObjectID] | None = None,
        subscribers_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.ParticipantType:  # type: ignore
        request = proto.UpdateParticipant(
            _id=id,
            room_id=room_id,
            state=state,
            viewed_ids=set(viewed_ids) if viewed_ids else set(),
            subscription_ids=set(subscription_ids) if subscription_ids else set(),
            subscribers_ids=set(subscribers_ids) if subscribers_ids else set(),
        )
        data = await info.context.participant.service.update(request)
        info.context.participant.loader.clear(id)
        return graphql.domain_to_participant(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def delete_participant(
        root: ParticipantQuery, info: Info[ParticipantQuery], id: scalar.ObjectID
    ) -> graphql.ParticipantType:  # type: ignore
        data = await info.context.participant.service.delete(
            proto.DeleteParticipant(_id=id)
        )
        info.context.participant.loader.clear(id)
        return graphql.domain_to_participant(data)
