import strawberry as sb

from src.adapter.external.graphql.type.user import UserType
from src.domain.model.preference import Preference, PreferenceKind, PreferenceStatus

PreferenceKindType = sb.enum(PreferenceKind)
PreferenceStatusType = sb.enum(PreferenceStatus)


@sb.experimental.pydantic.type(model=Preference)
class PreferenceType:
    id: sb.auto
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    kind: PreferenceKindType  # type: ignore
    status: PreferenceStatusType  # type: ignore

    user_id: sb.auto
    user: sb.Private[UserType]

    target_id: sb.auto
    target: sb.Private[UserType]
