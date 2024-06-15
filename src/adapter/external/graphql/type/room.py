import strawberry as sb

from src.adapter.external.graphql.type.user import GenderType
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

    creator_id: sb.auto
    editor_ids: sb.auto
