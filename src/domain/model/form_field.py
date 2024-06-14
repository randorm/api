import datetime
import re
from enum import Enum

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
    kind: FormFieldKind = FormFieldKind.TEXT

    re: re.Pattern[str] | None  # answer regex
    ex: str | None  # answer example


class ChoiceOption(pydantic.BaseModel):
    text: str = pydantic.Field(min_length=1)
    respondent_count: int = pydantic.Field(default=0, ge=0)


class ChoiceField(BaseFormField):
    kind: FormFieldKind = FormFieldKind.CHOICE
    options: list[ChoiceOption] = pydantic.Field(min_length=1)
    multiple: bool


type Field = TextFormField | ChoiceField


class BaseAnswer(pydantic.BaseModel):
    id: ObjectID = pydantic.Field(alias="_id")
    created_at: datetime.datetime
    updated_at: datetime.datetime
    deleted_at: datetime.datetime | None = pydantic.Field(default=None)

    field_id: ObjectID
    field_kind: FormFieldKind

    respondent_id: ObjectID


class TextAnswer(BaseAnswer):
    kind: FormFieldKind = FormFieldKind.TEXT
    text: str = pydantic.Field(min_length=1)
    text_entities: set[FormatEntity] = pydantic.Field(default_factory=set)


class ChoiceAnswer(BaseAnswer):
    kind: FormFieldKind = FormFieldKind.CHOICE
    option_ids: set[ObjectID]


type Answer = TextAnswer | ChoiceAnswer
