import datetime
from enum import StrEnum

import pydantic

from src.domain.model.scalar.object_id import ObjectID


class LanguageCode(StrEnum):
    """
    Language code enum in IETF tag format.
    For more information see: https://en.wikipedia.org/wiki/IETF_language_tag.
    """

    RU = "ru"
    EN = "en"


class Gender(StrEnum):
    MALE = "male"
    FEMALE = "female"


class Profile(pydantic.BaseModel):
    first_name: str = pydantic.Field(min_length=1)
    last_name: str | None = pydantic.Field(min_length=1)
    username: str | None = pydantic.Field(min_length=1)
    language_code: LanguageCode
    gender: Gender
    birthdate: datetime.date


class User(pydantic.BaseModel):
    id: ObjectID = pydantic.Field(alias="_id")
    telegram_id: int  # telegram id, should be serialized as int128
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: datetime.datetime | None = pydantic.Field(default=None)

    profile: Profile
    views: int = pydantic.Field(default=0, ge=0)
