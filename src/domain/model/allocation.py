import datetime
from enum import Enum
from typing import Literal

import pydantic

from src.domain.model.scalar.object_id import ObjectID


class AllocationState(str, Enum):
    CREATING = "creating"
    CREATED = "created"
    OPEN = "open"
    ROOMING = "rooming"
    ROOMED = "roomed"
    CLOSED = "closed"
    FAILED = "failed"


class BaseAllocation(pydantic.BaseModel):
    id: ObjectID = pydantic.Field(alias="_id")
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: datetime.datetime | None = pydantic.Field(default=None)

    name: str = pydantic.Field(min_length=1)
    due: datetime.datetime | None
    state: AllocationState

    form_field_ids: set[ObjectID] = pydantic.Field(default_factory=set)

    creator_id: ObjectID
    editor_ids: set[ObjectID] = pydantic.Field(default_factory=set)


class CreatingAllocation(BaseAllocation):
    state: Literal[AllocationState.CREATING] = AllocationState.CREATING


class CreatedAllocation(BaseAllocation):
    state: Literal[AllocationState.CREATED] = AllocationState.CREATED
    participant_ids: set[ObjectID]


class OpenAllocation(BaseAllocation):
    state: Literal[AllocationState.OPEN] = AllocationState.OPEN
    participant_ids: set[ObjectID]


class RoomingAllocation(BaseAllocation):
    state: Literal[AllocationState.ROOMING] = AllocationState.ROOMING
    participant_ids: set[ObjectID]


class RoomedAllocation(BaseAllocation):
    state: Literal[AllocationState.ROOMED] = AllocationState.ROOMED
    participant_ids: set[ObjectID]


class ClosedAllocation(BaseAllocation):
    state: Literal[AllocationState.CLOSED] = AllocationState.CLOSED
    participant_ids: set[ObjectID]


class FailedAllocation(BaseAllocation):
    state: Literal[AllocationState.FAILED] = AllocationState.FAILED


type Allocation = (
    CreatingAllocation
    | CreatedAllocation
    | OpenAllocation
    | RoomingAllocation
    | RoomedAllocation
    | ClosedAllocation
    | FailedAllocation
)

AllocationResolver = pydantic.TypeAdapter(
    type=Allocation,
    config=pydantic.ConfigDict(extra="ignore", from_attributes=True),
)
