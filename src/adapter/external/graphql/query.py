import strawberry as sb

from src.adapter.external.graphql.operation.allocation import AllocationQuery
from src.adapter.external.graphql.operation.form_field import FormFieldQuery
from src.adapter.external.graphql.operation.user import UserQuery


@sb.type
class Query(UserQuery, AllocationQuery, FormFieldQuery): ...
