import strawberry as sb

import src.domain.model.form_field as domain
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.type.format_entity import FormatEntityType
from src.domain.model.form_field import (
    BaseAnswer,
    BaseFormField,
    ChoiceAnswer,
    ChoiceFormField,
    ChoiceOption,
    FormFieldKind,
    TextAnswer,
    TextFormField,
)

FormFieldKindType = sb.enum(FormFieldKind)


@sb.experimental.pydantic.interface(model=BaseFormField)
class BaseFormFieldType:
    id: scalar.ObjectID
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    allocation_id: scalar.ObjectID
    # allocation: sb.Private[AllocationType]

    kind: FormFieldKindType  # type: ignore
    required: sb.auto
    frozen: sb.auto

    question: sb.auto
    question_entities: list[FormatEntityType]  # type: ignore

    respondent_count: sb.auto

    creator_id: scalar.ObjectID
    # creator: sb.Private[UserType]

    editors_ids: list[scalar.ObjectID]
    # editors: sb.Private[list[UserType]]


@sb.experimental.pydantic.type(model=TextFormField)
class TextFormFieldType(BaseFormFieldType):
    kind: FormFieldKindType = sb.field(default=FormFieldKindType.TEXT)  # type: ignore

    re: str
    ex: sb.auto


@sb.experimental.pydantic.type(model=ChoiceOption)
class ChoiceOptionType:
    text: sb.auto
    respondent_count: sb.auto


@sb.experimental.pydantic.type(model=ChoiceFormField)
class ChoiceFormFieldType(BaseFormFieldType):
    kind: FormFieldKindType = sb.field(default=FormFieldKindType.CHOICE)  # type: ignore

    options: list[ChoiceOptionType]
    multiple: sb.auto


FormFieldType = sb.union("FieldType", types=(TextFormFieldType, ChoiceFormFieldType))


def domain_to_form_field(data: domain.FormField) -> FormFieldType:  # type: ignore
    match data:
        case domain.TextFormField():
            return TextFormFieldType.from_pydantic(data)
        case domain.ChoiceFormField():
            return ChoiceFormFieldType.from_pydantic(data)


@sb.experimental.pydantic.interface(model=BaseAnswer)
class BaseAnswerType:
    id: scalar.ObjectID
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    field_id: scalar.ObjectID
    field_kind: FormFieldKindType  # type: ignore

    respondent_id: scalar.ObjectID
    # respondent: sb.Private[UserType]


@sb.experimental.pydantic.type(model=TextAnswer)
class TextAnswerType(BaseAnswerType):
    kind: FormFieldKindType = sb.field(default=FormFieldKindType.TEXT)  # type: ignore
    text: sb.auto
    text_entities: list[FormatEntityType]  # type: ignore


@sb.experimental.pydantic.type(model=ChoiceAnswer)
class ChoiceAnswerType(BaseAnswerType):
    kind: FormFieldKindType = sb.field(default=FormFieldKindType.CHOICE)  # type: ignore

    option_indexes: list[int]
    options: sb.Private[list[ChoiceOptionType]]


AnswerType = sb.union("AnswerType", types=(TextAnswerType, ChoiceAnswerType))
