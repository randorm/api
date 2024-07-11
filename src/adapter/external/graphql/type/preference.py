import strawberry as sb

from src.adapter.external.graphql import scalar
from src.domain.model.preference import Preference, PreferenceKind, PreferenceStatus

PreferenceKindType = sb.enum(PreferenceKind)
PreferenceStatusType = sb.enum(PreferenceStatus)


@sb.experimental.pydantic.type(model=Preference)
class PreferenceType:
    id: scalar.ObjectID
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    kind: PreferenceKindType  # type: ignore
    status: PreferenceStatusType  # type: ignore

    user_id: scalar.ObjectID
    # user: sb.Private[UserType]

    target_id: scalar.ObjectID
    # target: sb.Private[UserType]
