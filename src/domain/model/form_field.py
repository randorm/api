import datetime
import re
from enum import Enum
from typing import Literal

import pydantic

from src.domain.model.format_entity import FormatEntity
from src.domain.model.scalar.object_id import ObjectID


class FormFieldKind(str, Enum):
    TEXT = "text"
    CHOICE = "choice"


class BaseFormField(pydantic.BaseModel):
    id: ObjectID = pydantic.Field(alias="_id")
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: datetime.datetime | None = pydantic.Field(default=None)

    kind: FormFieldKind
    required: bool
    question: str = pydantic.Field(min_length=1)
    question_entities: set[FormatEntity] = pydantic.Field(default_factory=set)

    respondent_count: int = pydantic.Field(default=0, ge=0)

    creator_id: ObjectID
    editor_ids: set[ObjectID] = pydantic.Field(default_factory=set)


class TextFormField(BaseFormField):
    kind: Literal[FormFieldKind.TEXT] = FormFieldKind.TEXT

    re: re.Pattern[str] | None  # answer regex
    ex: str | None  # answer example


class ChoiceOption(pydantic.BaseModel):
    text: str = pydantic.Field(min_length=1)
    respondent_count: int = pydantic.Field(default=0, ge=0)


class ChoiceField(BaseFormField):
    kind: Literal[FormFieldKind.CHOICE] = FormFieldKind.CHOICE
    options: list[ChoiceOption] = pydantic.Field(min_length=1)
    multiple: bool


type FormField = TextFormField | ChoiceField

FormFieldResolver = pydantic.TypeAdapter(
    type=FormField,
    config=pydantic.ConfigDict(extra="ignore", from_attributes=True),
)


class BaseAnswer(pydantic.BaseModel):
    id: ObjectID = pydantic.Field(alias="_id")
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: datetime.datetime | None = pydantic.Field(default=None)

    field_id: ObjectID
    kind: FormFieldKind

    respondent_id: ObjectID


class TextAnswer(BaseAnswer):
    kind: Literal[FormFieldKind.TEXT] = FormFieldKind.TEXT
    text: str = pydantic.Field(min_length=1)
    text_entities: set[FormatEntity] = pydantic.Field(default_factory=set)


class ChoiceAnswer(BaseAnswer):
    kind: Literal[FormFieldKind.CHOICE] = FormFieldKind.CHOICE
    option_ids: set[ObjectID]


type Answer = TextAnswer | ChoiceAnswer

AnswerResolver = pydantic.TypeAdapter(
    type=Answer,
    config=pydantic.ConfigDict(extra="ignore", from_attributes=True),
)
