import datetime

import pydantic

from src.domain.model.scalar.object_id import ObjectID
from src.domain.model.user import Gender


class Room(pydantic.BaseModel):
    id: ObjectID = pydantic.Field(alias="_id")

    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: datetime.datetime | None = pydantic.Field(default=None)

    name: str = pydantic.Field(min_length=1)
    capacity: int = pydantic.Field(ge=0)
    occupied: int = pydantic.Field(ge=0)
    gender_restriction: Gender | None

    creator_id: ObjectID
    editors_ids: set[ObjectID] = pydantic.Field(default_factory=set)
