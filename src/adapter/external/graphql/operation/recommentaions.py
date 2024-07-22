from __future__ import annotations

from random import shuffle

import strawberry as sb

import src.domain.model as domain
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info
from src.adapter.external.graphql.tool.permission import DefaultPermissions
from src.adapter.external.graphql.type.participant import BaseParticipantType


@sb.type
class RecommendationsQuery:
    @sb.field(permission_classes=[DefaultPermissions])
    async def recommendations(
        root: RecommendationsQuery,
        info: Info[RecommendationsQuery],
        allocation_id: scalar.ObjectID,
    ) -> list[BaseParticipantType]:
        if info.context.user_id is None:
            raise Exception("User is not authenticated")

        participants = await info.context.participant.service.read_all()

        selected = [
            participant.id
            for participant in participants
            if participant.user_id != info.context.user_id
            and participant.allocation_id == allocation_id
            and participant.state == domain.ParticipantState.ACTIVE
        ]
        if not selected:
            return []

        shuffle(selected)

        return await info.context.participant.loader.load_many(selected[:10])
