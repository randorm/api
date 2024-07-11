from typing import TYPE_CHECKING, Annotated, Protocol

import strawberry as sb

from src.adapter.external.graphql import scalar

if TYPE_CHECKING:
    from src.adapter.external.graphql.tool.context import Context
    from src.adapter.external.graphql.type.form_field import FormFieldType
    from src.adapter.external.graphql.type.user import UserType

LazyFormFieldType = Annotated[
    "FormFieldType",  # type: ignore
    sb.lazy(module_path="src.adapter.external.graphql.type.form_field"),
]

LazyContext = Annotated[
    "Context",
    sb.lazy(module_path="src.adapter.external.graphql.tool.context"),
]

LazyUserType = Annotated[
    "UserType",
    sb.lazy(module_path="src.adapter.external.graphql.type.user"),
]


class WithFormFields(Protocol):
    form_fields_ids: list[scalar.ObjectID]


async def load_form_fields(
    root: WithFormFields,
    info: sb.Info[LazyContext, WithFormFields],
) -> list[LazyFormFieldType]:
    return await info.context.form_field.loader.load_many(root.form_fields_ids)


class WithCreator(Protocol):
    creator_id: scalar.ObjectID


async def load_creator(
    root: WithCreator,
    info: sb.Info[LazyContext, WithCreator],
) -> LazyUserType:
    return await info.context.user.loader.load(root.creator_id)


class WithEditors(Protocol):
    editors_ids: list[scalar.ObjectID]


async def load_editors(
    root: WithEditors,
    info: sb.Info[LazyContext, WithEditors],
) -> list[LazyUserType]:
    return await info.context.user.loader.load_many(root.editors_ids)


class WithParticipants(Protocol):
    participants_ids: list[scalar.ObjectID]


async def load_participants(
    root: WithParticipants,
    info: sb.Info[LazyContext, WithParticipants],
) -> list[LazyUserType]:
    return await info.context.user.loader.load_many(root.participants_ids)
