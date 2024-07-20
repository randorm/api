import strawberry as sb

from src.adapter.external.graphql.operation.allocation import (
    AllocationMutation,
    AllocationQuery,
)
from src.adapter.external.graphql.operation.form_field import (
    FormFieldMutation,
    FormFieldQuery,
)
from src.adapter.external.graphql.operation.participant import (
    ParticipantMutation,
    ParticipantQuery,
)
from src.adapter.external.graphql.operation.preference import (
    PreferenceMutation,
    PreferenceQuery,
)
from src.adapter.external.graphql.operation.room import RoomMutation, RoomQuery
from src.adapter.external.graphql.operation.user import UserMutation, UserQuery


@sb.type
class Query(
    AllocationQuery,
    FormFieldQuery,
    ParticipantQuery,
    PreferenceQuery,
    RoomQuery,
    UserQuery,
): ...


@sb.type
class Mutation(
    AllocationMutation,
    FormFieldMutation,
    ParticipantMutation,
    PreferenceMutation,
    RoomMutation,
    UserMutation,
): ...


SCHEMA = sb.Schema(query=Query, mutation=Mutation)
