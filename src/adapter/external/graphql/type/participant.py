import strawberry as sb

import src.domain.model.participant as domain
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool import resolver
from src.adapter.external.graphql.tool.permission import DefaultPermissions
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
    id: scalar.ObjectID = sb.field(name="id")
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    allocation_id: scalar.ObjectID
    allocation: resolver.LazyAllocationType = sb.field(  # type: ignore
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_allocation,
    )

    user_id: scalar.ObjectID
    user: resolver.LazyUserType = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_user,
    )

    state: ParticipantStateType  # type: ignore

    viewed_ids: list[scalar.ObjectID]
    viewed: list[resolver.LazyParticipantType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_viewed,
    )

    subscription_ids: list[scalar.ObjectID]
    subscriptions: list[resolver.LazyParticipantType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_subscriptions,
    )

    subscribers_ids: list[scalar.ObjectID]
    subscribers: list[resolver.LazyParticipantType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_subscribers,
    )

    answers: list[resolver.LazyAnswerType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_participant_answers,
    )


@sb.experimental.pydantic.type(model=CreatingParticipant)
class CreatingParticipantType(BaseParticipantType):
    state: ParticipantStateType = ParticipantStateType.CREATING  # type: ignore


@sb.experimental.pydantic.type(model=CreatedParticipant)
class CreatedParticipantType(BaseParticipantType):
    state: ParticipantStateType = ParticipantStateType.CREATED  # type: ignore


@sb.experimental.pydantic.type(model=ActiveParticipant)
class ActiveParticipantType(BaseParticipantType):
    state: ParticipantStateType = ParticipantStateType.ACTIVE  # type: ignore


@sb.experimental.pydantic.type(model=AllocatedParticipant)
class AllocatedParticipantType(BaseParticipantType):
    state: ParticipantStateType = ParticipantStateType.ALLOCATED  # type: ignore

    room_id: scalar.ObjectID
    room: resolver.LazyRoomType = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_room,
    )


ParticipantType = sb.union(
    "ParticipantType",
    types=(
        CreatingParticipantType,
        CreatedParticipantType,
        ActiveParticipantType,
        AllocatedParticipantType,
    ),
)


def domain_to_participant(data: domain.Participant) -> ParticipantType:  # type: ignore
    match data:
        case domain.CreatingParticipant():
            return CreatingParticipantType.from_pydantic(data)
        case domain.CreatedParticipant():
            return CreatedParticipantType.from_pydantic(data)
        case domain.ActiveParticipant():
            return ActiveParticipantType.from_pydantic(data)
        case domain.AllocatedParticipant():
            return AllocatedParticipantType.from_pydantic(data)
