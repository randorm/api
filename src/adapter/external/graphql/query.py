import strawberry.tools as sb_tools

from src.adapter.external.graphql.operation.user import UserQuery

GRAPHQL_QUERY = sb_tools.merge_types(
    "Query",
    (UserQuery,),
)
