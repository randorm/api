import strawberry as sb

from src.domain.model.scalar.object_id import ObjectID as DomainObjectID

ObjectID = sb.scalar(
    DomainObjectID,
    name="ObjectID",
    description="ObjectID scalar type",
    serialize=str,
    parse_value=DomainObjectID,
)
