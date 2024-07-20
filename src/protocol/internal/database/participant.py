from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

import src.domain.model.participant as domain
from src.domain.model.scalar.object_id import ObjectID
from src.protocol.internal.database.mixin import ExcludeFieldMixin


class CreateCreatingParticipant(ExcludeFieldMixin, domain.CreatingParticipant): ...


class CreateCreatedParticipant(ExcludeFieldMixin, domain.CreatedParticipant): ...


class CreateActiveParticipant(ExcludeFieldMixin, domain.ActiveParticipant): ...


class CreateAllocatedParticipant(ExcludeFieldMixin, domain.AllocatedParticipant): ...


type CreateParticipant = (
    CreateCreatingParticipant
    | CreateCreatedParticipant
    | CreateActiveParticipant
    | CreateAllocatedParticipant
)

CreateParticipantResolver = TypeAdapter(
    type=CreateParticipant,
    config=ConfigDict(extra="ignore", from_attributes=True),
)


class ReadParticipant(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateParticipant(ExcludeFieldMixin, domain.BaseParticipant):
    id: ObjectID = Field(alias="_id")  # type: ignore
    # exclude fields
    user_id: Literal[None] = None
    allocation_id: Literal[None] = None
    # optional fields
    viewed_ids: set[ObjectID] | None = Field(default=None)
    subscription_ids: set[ObjectID] | None = Field(default=None)
    subscribers_ids: set[ObjectID] | None = Field(default=None)
    state: domain.ParticipantState | None = Field(default=None)
    room_id: ObjectID | None = Field(default=None)


class DeleteParticipant(BaseModel):
    id: ObjectID = Field(alias="_id")


class ParticipantDatabaseProtocol(ABC):
    @abstractmethod
    async def create_participant(
        self, participant: CreateParticipant
    ) -> domain.Participant: ...

    @abstractmethod
    async def read_participant(
        self, participant: ReadParticipant
    ) -> domain.Participant: ...

    @abstractmethod
    async def update_participant(
        self, participant: UpdateParticipant
    ) -> domain.Participant: ...

    @abstractmethod
    async def delete_participant(
        self, participant: DeleteParticipant
    ) -> domain.Participant: ...

    @abstractmethod
    async def read_many_participants(
        self, participants: list[ReadParticipant]
    ) -> list[domain.Participant | None]: ...
