from enum import StrEnum
from typing import Annotated

import strawberry as sb

from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.type.form_field import FormFieldType
from src.adapter.external.graphql.type.user import UserType
from src.domain.model.allocation import (
    AllocationState,
    BaseAllocation,
    ClosedAllocation,
    CreatedAllocation,
    CreatingAllocation,
    FailedAllocation,
    OpenAllocation,
    RoomedAllocation,
    RoomingAllocation,
)


@sb.enum
class AllocationStateType(StrEnum):
    CREATING = AllocationState.CREATING.value
    CREATED = AllocationState.CREATED.value
    OPEN = AllocationState.OPEN.value
    ROOMING = AllocationState.ROOMING.value
    ROOMED = AllocationState.ROOMED.value
    CLOSED = AllocationState.CLOSED.value
    FAILED = AllocationState.FAILED.value


@sb.experimental.pydantic.interface(model=BaseAllocation)
class BaseAllocationType:
    id: scalar.ObjectID
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    name: sb.auto
    due: sb.auto
    state: AllocationStateType

    form_fields_ids: list[scalar.ObjectID]
    form_fields: sb.Private[list[FormFieldType]]

    creator_id: scalar.ObjectID
    creator: sb.Private[UserType]

    editors_ids: list[scalar.ObjectID]
    editors: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=CreatingAllocation)
class CreatingAllocationType(BaseAllocationType):
    state: AllocationStateType = AllocationStateType.CREATING


@sb.experimental.pydantic.type(model=CreatedAllocation)
class CreatedAllocationType(BaseAllocationType):
    state: AllocationStateType = AllocationStateType.CREATED

    participants_ids: list[scalar.ObjectID]
    participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=OpenAllocation)
class OpenAllocationType(BaseAllocationType):
    state: AllocationStateType = AllocationStateType.OPEN

    participants_ids: list[scalar.ObjectID]
    participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=RoomingAllocation)
class RoomingAllocationType(BaseAllocationType):
    state: AllocationStateType = AllocationStateType.ROOMING

    participants_ids: list[scalar.ObjectID]
    participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=RoomedAllocation)
class RoomedAllocationType(BaseAllocationType):
    state: AllocationStateType = AllocationStateType.ROOMED

    participants_ids: list[scalar.ObjectID]
    participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=ClosedAllocation)
class ClosedAllocationType(BaseAllocationType):
    state: AllocationStateType = AllocationStateType.CLOSED

    participants_ids: list[scalar.ObjectID]
    participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=FailedAllocation)
class FailedAllocationType(BaseAllocationType):
    state: AllocationStateType = AllocationStateType.FAILED


type AllocationType = Annotated[
    CreatingAllocationType
    | CreatedAllocationType
    | OpenAllocationType
    | RoomingAllocationType
    | RoomedAllocationType
    | ClosedAllocationType
    | FailedAllocationType,
    sb.union("AllocationType"),
]
