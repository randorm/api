import datetime
from enum import StrEnum
from typing import Literal

import pydantic

from src.domain.model.scalar.object_id import ObjectID


class ParticipantState(StrEnum):
    CREATING = "creating"  # field ids unfrozen
    CREATED = "created"  # field ids frozen
    ACTIVE = "active"  # feed opened
    ALLOCATED = "allocated"  # allocated to room


class BaseParticipant(pydantic.BaseModel):
    id: ObjectID = pydantic.Field(alias="_id")
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: datetime.datetime | None = pydantic.Field(default=None)

    allocation_id: ObjectID
    user_id: ObjectID

    state: ParticipantState

    viewed_ids: set[ObjectID]
    subscription_ids: set[ObjectID]
    subscribers_ids: set[ObjectID]


class CreatingParticipant(BaseParticipant):
    state: Literal[ParticipantState.CREATING] = ParticipantState.CREATING


class CreatedParticipant(BaseParticipant):
    state: Literal[ParticipantState.CREATED] = ParticipantState.CREATED


class ActiveParticipant(BaseParticipant):
    state: Literal[ParticipantState.ACTIVE] = ParticipantState.ACTIVE


class AllocatedParticipant(BaseParticipant):
    state: Literal[ParticipantState.ALLOCATED] = ParticipantState.ALLOCATED


type Participant = (
    CreatingParticipant | CreatedParticipant | ActiveParticipant | AllocatedParticipant
)


ParticipantResolver = pydantic.TypeAdapter(
    type=Participant,
    config=pydantic.ConfigDict(extra="ignore", from_attributes=True),
)
