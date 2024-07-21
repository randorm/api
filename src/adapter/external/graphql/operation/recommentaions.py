from __future__ import annotations

from random import shuffle

import strawberry as sb

import src.domain.model as domain
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info
from src.adapter.external.graphql.type.participant import BaseParticipantType


@sb.type
class RecommendationsQuery:
    @sb.field
    async def recommendations(
        root: RecommendationsQuery,
        info: Info[RecommendationsQuery],
        user_id: scalar.ObjectID,
        allocation_id: scalar.ObjectID,
    ) -> list[BaseParticipantType]:
        participants = await info.context.participant.service.read_all()

        selected = [
            participant.id
            for participant in participants
            if participant.user_id != user_id
            and participant.allocation_id == allocation_id
            and participant.state == domain.ParticipantState.ACTIVE
        ]
        if not selected:
            return []

        shuffle(selected)

        return await info.context.participant.loader.load_many(selected[:10])
