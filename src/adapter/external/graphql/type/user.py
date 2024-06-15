from enum import StrEnum

import strawberry as sb

from src.domain.model.user import Gender, LanguageCode, Profile, User


@sb.enum
class LanguageCodeType(StrEnum):
    RU = LanguageCode.RU.value
    EN = LanguageCode.EN.value


@sb.enum
class GenderType(StrEnum):
    MALE = Gender.MALE.value
    FEMALE = Gender.FEMALE.value


@sb.experimental.pydantic.type(model=Profile)
class ProfileType:
    first_name: sb.auto
    last_name: sb.auto
    username: sb.auto
    language_code: sb.auto
    gender: GenderType
    birthdate: sb.auto


@sb.experimental.pydantic.type(model=User)
class UserType:
    id: sb.auto
    tid: sb.auto
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto
    profile: ProfileType
    views: sb.auto
