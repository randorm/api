import datetime
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from src.domain.model.allocation import (
    Allocation,
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
from src.domain.model.scalar.object_id import ObjectID
from src.protocol.internal.database.mixin import ExcludeFieldMixin


class CreateCreatingAllocation(ExcludeFieldMixin, CreatingAllocation): ...


class CreateCreatedAllocation(ExcludeFieldMixin, CreatedAllocation): ...


class CreateOpenAllocation(ExcludeFieldMixin, OpenAllocation): ...


class CreateRoomingAllocation(ExcludeFieldMixin, RoomingAllocation): ...


class CreateRoomedAllocation(ExcludeFieldMixin, RoomedAllocation): ...


class CreateClosedAllocation(ExcludeFieldMixin, ClosedAllocation): ...


class CreateFailedAllocation(ExcludeFieldMixin, FailedAllocation): ...


type CreateAllocation = (
    CreateCreatingAllocation
    | CreateCreatedAllocation
    | CreateOpenAllocation
    | CreateRoomingAllocation
    | CreateRoomedAllocation
    | CreateClosedAllocation
    | CreateFailedAllocation
)


class ReadAllocation(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateAllocation(ExcludeFieldMixin, BaseAllocation):
    id: ObjectID = Field(alias="_id")
    # optinal fields
    name: str | None = Field(default=None)
    due: datetime.datetime | None = Field(default=None)
    state: AllocationState | None = Field(default=None)
    field_ids: set[ObjectID] | None = Field(default=None)
    editor_ids: set[ObjectID] | None = Field(default=None)
    participant_ids: set[ObjectID] | None = Field(default=None)
    # creator_id: ObjectID | None = Field(default=None)


class DeleteAllocation(BaseModel):
    id: ObjectID = Field(alias="_id")


class AllocationDatabaseProtocol(ABC):
    @abstractmethod
    async def create_allocation(self, allocation: CreateAllocation) -> Allocation: ...

    @abstractmethod
    async def read_allocation(self, allocation: ReadAllocation) -> Allocation: ...

    @abstractmethod
    async def update_allocation(self, allocation: UpdateAllocation) -> Allocation: ...

    @abstractmethod
    async def delete_allocation(self, allocation: DeleteAllocation) -> Allocation: ...
