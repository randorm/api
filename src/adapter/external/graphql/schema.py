import strawberry as sb

from src.adapter.external.graphql.operation.allocation import (
    AllocationMutation,
    AllocationQuery,
)
from src.adapter.external.graphql.operation.feed import FeedMutation
from src.adapter.external.graphql.operation.form_field import (
    AnswerMutation,
    AnswerQuery,
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
from src.adapter.external.graphql.operation.recommentaions import RecommendationsQuery
from src.adapter.external.graphql.operation.room import RoomMutation, RoomQuery
from src.adapter.external.graphql.operation.user import UserMutation, UserQuery


@sb.type
class Query(
    AllocationQuery,
    AnswerQuery,
    FormFieldQuery,
    ParticipantQuery,
    PreferenceQuery,
    RoomQuery,
    UserQuery,
    RecommendationsQuery,
): ...


@sb.type
class Mutation(
    AllocationMutation,
    AnswerMutation,
    FormFieldMutation,
    ParticipantMutation,
    PreferenceMutation,
    RoomMutation,
    UserMutation,
    FeedMutation,
): ...


SCHEMA = sb.Schema(query=Query, mutation=Mutation)
