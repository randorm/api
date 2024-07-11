import strawberry as sb

from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool import resolver
from src.adapter.external.graphql.tool.permission import DefaultPermissions
from src.adapter.external.graphql.tool.resolver import LazyUserType
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

    gender_restriction: GenderType  # type: ignore

    creator_id: scalar.ObjectID
    creator: LazyUserType = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_creator,
    )

    editors_ids: list[scalar.ObjectID]
    editors: list[LazyUserType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_editors,
    )
