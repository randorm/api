from __future__ import annotations

import strawberry as sb

import src.protocol.internal.database.participant as proto
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info
from src.adapter.external.graphql.tool.permission import DefaultPermissions
from src.adapter.external.graphql.type.participant import (
    BaseParticipantType,
    domain_to_participant,
)


@sb.type
class FeedMutation:
    @sb.mutation(permission_classes=[DefaultPermissions])
    async def mark_viewed(
        root: FeedMutation, info: Info[FeedMutation], id: scalar.ObjectID
    ) -> BaseParticipantType:
        participants = await info.context.participant.service.read_all()

        current = None
        for participant in participants:
            if participant.user_id == info.context.user_id:
                current = participant
                break
        if current is None:
            raise Exception("User is not participant")

        current = await info.context.participant.loader.load(current.id)
        data = await info.context.participant.service.update(
            proto.UpdateParticipant(
                _id=current.id, viewed_ids=set(current.viewed_ids) | {id}
            )
        )
        info.context.participant.loader.clear(current.id)
        return domain_to_participant(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def unsubscribe(
        root: FeedMutation, info: Info[FeedMutation], id: scalar.ObjectID
    ) -> BaseParticipantType:
        participants = await info.context.participant.service.read_all()

        current = None
        for participant in participants:
            if participant.user_id == info.context.user_id:
                current = participant
                break
        if current is None:
            raise Exception("User is not participant")

        current = await info.context.participant.loader.load(current.id)
        other = await info.context.participant.loader.load(id)

        data_current = await info.context.participant.service.update(
            proto.UpdateParticipant(
                _id=current.id, subscription_ids=set(current.subscription_ids) - {id}
            )
        )

        data_other = await info.context.participant.service.update(
            proto.UpdateParticipant(
                _id=other.id, subscribers_ids=set(other.subscribers_ids) - {current.id}
            )
        )
        _ = data_other

        info.context.participant.loader.clear_many([current.id, other.id])
        return domain_to_participant(data_current)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def subscribe(
        root: FeedMutation, info: Info[FeedMutation], id: scalar.ObjectID
    ) -> BaseParticipantType:
        participants = await info.context.participant.service.read_all()

        current = None
        for participant in participants:
            if participant.user_id == info.context.user_id:
                current = participant
                break
        if current is None:
            raise Exception("User is not participant")

        current = await info.context.participant.loader.load(current.id)
        other = await info.context.participant.loader.load(id)

        data_current = await info.context.participant.service.update(
            proto.UpdateParticipant(
                _id=current.id, subscription_ids=set(current.subscription_ids) | {id}
            )
        )

        data_other = await info.context.participant.service.update(
            proto.UpdateParticipant(
                _id=other.id, subscribers_ids=set(other.subscribers_ids) | {current.id}
            )
        )
        _ = data_other

        info.context.participant.loader.clear_many([current.id, other.id])
        return domain_to_participant(data_current)
