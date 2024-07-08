import datetime
from enum import StrEnum

from pydantic import BaseModel, Field

from src.domain.model.scalar.object_id import ObjectID


class PreferenceKind(StrEnum):
    MATRIMONY = "matrimony"
    COURTSHIP = "courtship"
    FRIENDSHIP = "friendship"


class PreferenceStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Preference(BaseModel):
    id: ObjectID = Field(alias="_id")
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: datetime.datetime | None = Field(default=None)

    kind: PreferenceKind
    status: PreferenceStatus

    user_id: ObjectID
    target_id: ObjectID
