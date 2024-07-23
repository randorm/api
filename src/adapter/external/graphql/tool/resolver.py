from typing import TYPE_CHECKING, Annotated, Protocol

import strawberry as sb

from src.adapter.external.graphql import scalar

if TYPE_CHECKING:
    from src.adapter.external.graphql.tool.context import Context
    from src.adapter.external.graphql.type.allocation import (
        BaseAllocationType,
    )
    from src.adapter.external.graphql.type.form_field import (
        BaseAnswerType,
        BaseFormFieldType,
        ChoiceOptionType,
    )
    from src.adapter.external.graphql.type.participant import (
        BaseParticipantType,
    )
    from src.adapter.external.graphql.type.room import RoomType
    from src.adapter.external.graphql.type.user import UserType


LazyFormFieldType = Annotated[
    "BaseFormFieldType",  # type: ignore
    sb.lazy(module_path="src.adapter.external.graphql.type.form_field"),
]

LazyContext = Annotated[
    "Context",
    sb.lazy(module_path="src.adapter.external.graphql.tool.context"),
]

LazyUserType = Annotated[
    "UserType",
    sb.lazy(module_path="src.adapter.external.graphql.type.user"),
]

LazyAllocationType = Annotated[
    "BaseAllocationType",  # type: ignore
    sb.lazy(module_path="src.adapter.external.graphql.type.allocation"),
]

LazyRoomType = Annotated[
    "RoomType",
    sb.lazy(module_path="src.adapter.external.graphql.type.room"),
]

LazyParticipantType = Annotated[
    "BaseParticipantType",  # type: ignore
    sb.lazy(module_path="src.adapter.external.graphql.type.participant"),
]

LazyChoiceOptionType = Annotated[
    "ChoiceOptionType",  # type: ignore
    sb.lazy(module_path="src.adapter.external.graphql.type.form_field"),
]

LazyAnswerType = Annotated[
    "BaseAnswerType",  # type: ignore
    sb.lazy(module_path="src.adapter.external.graphql.type.form_field"),
]


class WithFormFields(Protocol):
    form_fields_ids: list[scalar.ObjectID]


async def load_form_fields(
    root: WithFormFields,
    info: sb.Info[LazyContext, WithFormFields],
) -> list[LazyFormFieldType]:
    return await info.context.form_field.loader.load_many(root.form_fields_ids)


class WithCreator(Protocol):
    creator_id: scalar.ObjectID


async def load_creator(
    root: WithCreator,
    info: sb.Info[LazyContext, WithCreator],
) -> LazyUserType:
    return await info.context.user.loader.load(root.creator_id)


class WithEditors(Protocol):
    editors_ids: list[scalar.ObjectID]


async def load_editors(
    root: WithEditors,
    info: sb.Info[LazyContext, WithEditors],
) -> list[LazyUserType]:
    return await info.context.user.loader.load_many(root.editors_ids)


class WithParticipants(Protocol):
    participants_ids: list[scalar.ObjectID]


async def load_participants(
    root: WithParticipants,
    info: sb.Info[LazyContext, WithParticipants],
) -> list[LazyUserType]:
    return await info.context.user.loader.load_many(root.participants_ids)


class WithRespondent(Protocol):
    respondent_id: scalar.ObjectID


async def load_respondent(
    root: WithRespondent,
    info: sb.Info[LazyContext, WithRespondent],
) -> LazyParticipantType:
    return await info.context.participant.loader.load(root.respondent_id)


class WithAllocation(Protocol):
    allocation_id: scalar.ObjectID


async def load_allocation(
    root: WithAllocation,
    info: sb.Info[LazyContext, WithAllocation],
) -> LazyAllocationType:
    return await info.context.allocation.loader.load(root.allocation_id)


class WithUser(Protocol):
    user_id: scalar.ObjectID


async def load_user(
    root: WithUser,
    info: sb.Info[LazyContext, WithUser],
) -> LazyUserType:
    return await info.context.user.loader.load(root.user_id)


class WithViewed(Protocol):
    viewed_ids: list[scalar.ObjectID]


async def load_viewed(
    root: WithViewed,
    info: sb.Info[LazyContext, WithViewed],
) -> list[LazyParticipantType]:
    return await info.context.participant.loader.load_many(root.viewed_ids)


class WithSubscriptions(Protocol):
    subscription_ids: list[scalar.ObjectID]


async def load_subscriptions(
    root: WithSubscriptions,
    info: sb.Info[LazyContext, WithSubscriptions],
) -> list[LazyParticipantType]:
    return await info.context.participant.loader.load_many(root.subscription_ids)


class WithSubscribers(Protocol):
    subscriber_ids: list[scalar.ObjectID]


async def load_subscribers(
    root: WithSubscribers,
    info: sb.Info[LazyContext, WithSubscribers],
) -> list[LazyParticipantType]:
    return await info.context.participant.loader.load_many(root.subscriber_ids)


class WithRoom(Protocol):
    room_id: scalar.ObjectID


async def load_room(
    root: WithRoom,
    info: sb.Info[LazyContext, WithRoom],
) -> LazyRoomType:
    return await info.context.room.loader.load(root.room_id)


class WithTarget(Protocol):
    target_id: scalar.ObjectID


async def load_target(
    root: WithTarget,
    info: sb.Info[LazyContext, WithTarget],
) -> LazyUserType:
    return await info.context.user.loader.load(root.target_id)


class WithOptions(Protocol):
    form_field_id: scalar.ObjectID
    option_indexes: list[scalar.ObjectID]


async def load_options(
    root: WithOptions,
    info: sb.Info[LazyContext, WithOptions],
) -> list[LazyChoiceOptionType]:
    form_field = await info.context.form_field.loader.load(root.form_field_id)

    selected = []
    for option_idx in root.option_indexes:
        selected.append(form_field.options[option_idx])

    return selected


class WithID(Protocol):
    id: scalar.ObjectID  # should be used only for participant type


async def load_participant_answers(
    root: WithID, info: sb.Info[LazyContext, WithID]
) -> list[LazyAnswerType]:
    answers = await info.context.answer.service.read_all()
    selected = [answer.id for answer in answers if answer.respondent_id == root.id]
    return await info.context.answer.loader.load_many(selected)


class WithFormFieldId(Protocol):
    form_field_id: scalar.ObjectID


async def load_form_field(
    root: WithFormFieldId,
    info: sb.Info[LazyContext, WithFormFieldId],
) -> LazyFormFieldType:
    return await info.context.form_field.loader.load(root.form_field_id)
