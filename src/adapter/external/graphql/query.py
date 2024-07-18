import strawberry as sb

from src.adapter.external.graphql.operation.allocation import AllocationQuery
from src.adapter.external.graphql.operation.form_field import FormFieldQuery
from src.adapter.external.graphql.operation.participant import ParticipantQuery
from src.adapter.external.graphql.operation.preference import PreferenceQuery
from src.adapter.external.graphql.operation.room import RoomQuery
from src.adapter.external.graphql.operation.user import UserQuery


@sb.type
class Query(
    AllocationQuery,
    FormFieldQuery,
    ParticipantQuery,
    PreferenceQuery,
    RoomQuery,
    UserQuery,
): ...
