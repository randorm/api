import strawberry as sb

from src.adapter.external.graphql import scalar
from src.domain.model.user import Gender, LanguageCode, Profile, User

LanguageCodeType = sb.enum(LanguageCode)

GenderType = sb.enum(Gender)


@sb.experimental.pydantic.type(model=Profile)
class ProfileType:
    first_name: sb.auto
    last_name: sb.auto
    username: sb.auto
    language_code: LanguageCodeType  # type: ignore
    gender: GenderType  # type: ignore
    birthdate: sb.auto


@sb.experimental.pydantic.type(model=User)
class UserType:
    id: scalar.ObjectID = sb.field(name="id")
    telegram_id: sb.auto
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto
    profile: ProfileType
    views: sb.auto
