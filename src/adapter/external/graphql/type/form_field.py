from enum import StrEnum
from typing import Annotated

import strawberry as sb

from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.type.format_entity import FormatEntityType
from src.adapter.external.graphql.type.user import UserType
from src.domain.model.form_field import (
    BaseAnswer,
    BaseFormField,
    ChoiceAnswer,
    ChoiceField,
    ChoiceOption,
    FormFieldKind,
    TextAnswer,
    TextFormField,
)


@sb.enum
class FormFieldKindType(StrEnum):
    TEXT = FormFieldKind.TEXT.value
    CHOICE = FormFieldKind.CHOICE.value


@sb.experimental.pydantic.type(model=BaseFormField)
class BaseFormFieldType:
    id: scalar.ObjectID
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    kind: FormFieldKindType
    required: sb.auto
    question: sb.auto
    question_entities: list[FormatEntityType]

    respondent_count: sb.auto

    creator: UserType
    editors: list[UserType]


@sb.experimental.pydantic.type(model=TextFormField)
class TextFormFieldType(BaseFormFieldType):
    kind: FormFieldKindType = FormFieldKindType.TEXT

    re: sb.auto
    ex: sb.auto


@sb.experimental.pydantic.type(model=ChoiceOption)
class ChoiceOptionType:
    text: sb.auto
    respondent_count: sb.auto


@sb.experimental.pydantic.type(model=ChoiceField)
class ChoiceFormFieldType(BaseFormFieldType):
    kind: FormFieldKindType = FormFieldKindType.CHOICE
    options: list[ChoiceOptionType]
    multiple: sb.auto


type FormFieldType = Annotated[
    TextFormFieldType | ChoiceFormFieldType,
    sb.union("FieldType"),
]


@sb.experimental.pydantic.type(model=BaseAnswer)
class BaseAnswerType:
    id: scalar.ObjectID
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    field_id: sb.auto
    field_kind: FormFieldKindType

    respondent: UserType


@sb.experimental.pydantic.type(model=TextAnswer)
class TextAnswerType(BaseAnswerType):
    kind: FormFieldKindType = FormFieldKindType.TEXT
    text: sb.auto
    text_entities: list[FormatEntityType]


@sb.experimental.pydantic.type(model=ChoiceAnswer)
class ChoiceAnswerType(BaseAnswerType):
    kind: FormFieldKindType = FormFieldKindType.CHOICE
    choices: list[ChoiceOptionType]


type AnswerType = Annotated[
    TextAnswerType | ChoiceAnswerType,
    sb.union("AnswerType"),
]
