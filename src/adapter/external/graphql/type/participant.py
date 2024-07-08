from typing import Literal

import strawberry as sb

from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.type.allocation import AllocationType
from src.adapter.external.graphql.type.room import RoomType
from src.adapter.external.graphql.type.user import UserType
from src.domain.model.participant import (
    ActiveParticipant,
    AllocatedParticipant,
    BaseParticipant,
    CreatedParticipant,
    CreatingParticipant,
    ParticipantState,
)

ParticipantStateType = sb.enum(ParticipantState)


@sb.experimental.pydantic.interface(model=BaseParticipant)
class BaseParticipantType:
    id: sb.auto
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    allocation_id: sb.auto
    allocation: sb.Private[AllocationType]

    user_id: sb.auto
    user: sb.Private[UserType]

    state: ParticipantStateType  # type: ignore

    viewed_ids: list[scalar.ObjectID]
    viewed: sb.Private[list[UserType]]

    subscription_ids: list[scalar.ObjectID]
    subscriptions: sb.Private[list[UserType]]

    subscribers_ids: list[scalar.ObjectID]
    subscribers: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=CreatingParticipant)
class CreatingParticipantType(BaseParticipantType):
    state: Literal[ParticipantStateType.CREATING] = ParticipantStateType.CREATING


@sb.experimental.pydantic.type(model=CreatedParticipant)
class CreatedParticipantType(BaseParticipantType):
    state: Literal[ParticipantStateType.CREATED] = ParticipantStateType.CREATED


@sb.experimental.pydantic.type(model=ActiveParticipant)
class ActiveParticipantType(BaseParticipantType):
    state: Literal[ParticipantStateType.ACTIVE] = ParticipantStateType.ACTIVE


@sb.experimental.pydantic.type(model=AllocatedParticipant)
class AllocatedParticipantType(BaseParticipantType):
    state: Literal[ParticipantStateType.ALLOCATED] = ParticipantStateType.ALLOCATED

    room_id: sb.auto
    room: sb.Private[RoomType]
