import strawberry as sb

from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.type.user import GenderType, UserType
from src.domain.model.room import Room


@sb.experimental.pydantic.type(model=Room)
class RoomType:
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    name: sb.auto
    capacity: sb.auto
    occupied: sb.auto
    gender_restriction: GenderType

    creator_id: scalar.ObjectID
    creator: sb.Private[UserType]

    editors_ids: list[scalar.ObjectID]
    editors: sb.Private[list[UserType]]
