import datetime
from abc import ABC, abstractmethod

from pydantic import BaseModel, Field, SkipJsonSchema

from src.domain.model.allocation import Allocation, AllocationState, BaseAllocation
from src.domain.model.scalar.object_id import ObjectID


class CreateAllocationWithParticipands(BaseAllocation):
    participant_ids: set[ObjectID]
    # excluded fields
    id: SkipJsonSchema[int | None] = Field(default=None, exclude=True)  # type: ignore
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


class CreateAllocationWithoutParticipands(BaseAllocation):
    # excluded fields
    id: SkipJsonSchema[int | None] = Field(default=None, exclude=True)  # type: ignore
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


type CreateAllocation = CreateAllocationWithParticipands | CreateAllocationWithoutParticipands


class ReadAllocation(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateAllocation(BaseAllocation):
    # optinal fields
    name: str | None = Field(default=None)
    due: datetime.datetime | None = Field(default=None)
    state: AllocationState | None = Field(default=None)
    field_ids: set[ObjectID] | None = Field(default=None)
    editor_ids: set[ObjectID] | None = Field(default=None)
    participant_ids: set[ObjectID] | None = Field(default=None)
    # creator_id: ObjectID | None = Field(default=None)

    # excluded fields
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


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
