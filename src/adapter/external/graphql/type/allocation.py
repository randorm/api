from typing import Annotated, Literal

import strawberry as sb

from src.adapter.external.graphql import scalar
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

AllocationStateType = sb.enum(AllocationState)


@sb.experimental.pydantic.interface(model=BaseAllocation)
class BaseAllocationType:
    id: scalar.ObjectID
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    name: sb.auto
    due: sb.auto
    state: AllocationStateType  # type: ignore

    form_fields_ids: list[scalar.ObjectID]
    # form_fields: sb.Private[list[FormFieldType]]

    creator_id: scalar.ObjectID
    # creator: sb.Private[UserType]

    editors_ids: list[scalar.ObjectID]
    # editors: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=CreatingAllocation)
class CreatingAllocationType(BaseAllocationType):
    state: Literal[AllocationStateType.CREATING] = AllocationStateType.CREATING


@sb.experimental.pydantic.type(model=CreatedAllocation)
class CreatedAllocationType(BaseAllocationType):
    state: Literal[AllocationStateType.CREATED] = AllocationStateType.CREATED

    participants_ids: list[scalar.ObjectID]
    # participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=OpenAllocation)
class OpenAllocationType(BaseAllocationType):
    state: Literal[AllocationStateType.OPEN] = AllocationStateType.OPEN

    participants_ids: list[scalar.ObjectID]
    # participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=RoomingAllocation)
class RoomingAllocationType(BaseAllocationType):
    state: Literal[AllocationStateType.ROOMING] = AllocationStateType.ROOMING

    participants_ids: list[scalar.ObjectID]
    # participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=RoomedAllocation)
class RoomedAllocationType(BaseAllocationType):
    state: Literal[AllocationStateType.ROOMED] = AllocationStateType.ROOMED

    participants_ids: list[scalar.ObjectID]
    # participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=ClosedAllocation)
class ClosedAllocationType(BaseAllocationType):
    state: Literal[AllocationStateType.CLOSED] = AllocationStateType.CLOSED

    participants_ids: list[scalar.ObjectID]
    # participants: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=FailedAllocation)
class FailedAllocationType(BaseAllocationType):
    state: Literal[AllocationStateType.FAILED] = AllocationStateType.FAILED


AllocationType = Annotated[
    CreatingAllocationType
    | CreatedAllocationType
    | OpenAllocationType
    | RoomingAllocationType
    | RoomedAllocationType
    | ClosedAllocationType
    | FailedAllocationType,
    sb.union("AllocationType"),
]
