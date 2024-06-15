import datetime
from enum import Enum

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
    state: AllocationState = AllocationState.CREATING


class CreatedAllocation(BaseAllocation):
    state: AllocationState = AllocationState.CREATED
    participant_ids: set[ObjectID]


class OpenAllocation(BaseAllocation):
    state: AllocationState = AllocationState.OPEN
    participant_ids: set[ObjectID]


class RoomingAllocation(BaseAllocation):
    state: AllocationState = AllocationState.ROOMING
    participant_ids: set[ObjectID]


class RoomedAllocation(BaseAllocation):
    state: AllocationState = AllocationState.ROOMED
    participant_ids: set[ObjectID]


class ClosedAllocation(BaseAllocation):
    state: AllocationState = AllocationState.CLOSED
    participant_ids: set[ObjectID]


class FailedAllocation(BaseAllocation):
    state: AllocationState = AllocationState.FAILED


type Allocation = (
    CreatingAllocation
    | CreatedAllocation
    | OpenAllocation
    | RoomingAllocation
    | RoomedAllocation
    | ClosedAllocation
    | FailedAllocation
)
