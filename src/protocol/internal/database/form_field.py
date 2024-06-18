import datetime
from abc import ABC, abstractmethod
from re import Pattern

from pydantic import BaseModel, Field, SkipJsonSchema

from src.domain.model.form_field import (
    Answer,
    ChoiceAnswer,
    ChoiceField,
    ChoiceOption,
    FormField,
    FormFieldKind,
    TextAnswer,
    TextFormField,
)
from src.domain.model.format_entity import FormatEntity
from src.domain.model.scalar.object_id import ObjectID


class CreateTextFormField(TextFormField):
    # excluded fields
    id: SkipJsonSchema[int | None] = Field(default=None, exclude=True)  # type: ignore
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


class CreateChoiceFormField(ChoiceField):
    # excluded fields
    id: SkipJsonSchema[int | None] = Field(default=None, exclude=True)  # type: ignore
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


type CreateFormField = CreateTextFormField | CreateChoiceFormField


class ReadFormField(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateTextFormField(TextFormField):
    # optional fields
    required: bool | None = Field(default=None)
    question: str | None = Field(default=None)
    question_entities: set[FormatEntity] | None = Field(default=None)
    respondent_count: int | None = Field(default=None)
    editor_ids: set[ObjectID] | None = Field(default=None)
    re: Pattern[str] | None = Field(default=None)
    ex: str | None = Field(default=None)
    # creator_id: ObjectID | None = Field(default=None)

    # excluded fields
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


class UpdateChoiceOption(ChoiceOption):
    text: str | None = Field(default=None)
    respondent_count: int | None = Field(default=None)


class UpdateChoiceFormField(ChoiceField):
    options: list[UpdateChoiceOption] | None = Field(default=None)
    multiple: bool | None = Field(default=None)

    # excluded fields
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


type UpdateFormField = UpdateTextFormField | UpdateChoiceFormField


class DeleteFormField(BaseModel):
    id: ObjectID = Field(alias="_id")


class CreateTextAnswer(TextAnswer):
    # excluded fields
    id: SkipJsonSchema[int | None] = Field(default=None, exclude=True)  # type: ignore
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


class CreateChoiseAnswer(ChoiceAnswer):
    # excluded fields
    id: SkipJsonSchema[int | None] = Field(default=None, exclude=True)  # type: ignore
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


type CreateAnswer = CreateTextAnswer | CreateChoiseAnswer


class ReadAnswer(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateTextAnswer(TextAnswer):
    text: str | None = Field(default=None)
    text_entities: set[FormatEntity] | None = Field(default=None)
    field_id: ObjectID | None = Field(default=None)
    field_kind: FormFieldKind | None = Field(default=None)
    # respondent_id: ObjectID | None = Field(default=None)

    # excluded fields
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


class UpdateChoiseAnswer(ChoiceAnswer):
    option_ids: set[ObjectID] | None = Field(default=None)
    field_id: ObjectID | None = Field(default=None)
    field_kind: FormFieldKind | None = Field(default=None)
    # respondent_id: ObjectID | None = Field(default=None)

    # excluded fields
    created_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime.datetime | None] = Field(default=None, exclude=True)  # type: ignore


type UpdateAnswer = UpdateTextAnswer | UpdateChoiseAnswer


class DeleteAnswer(BaseModel):
    id: ObjectID = Field(alias="_id")


class FormFieldDatabaseProtocol(ABC):
    @abstractmethod
    async def create_form_field(self, form_field: CreateFormField) -> FormField: ...

    @abstractmethod
    async def read_form_field(self, form_field: ReadFormField) -> FormField: ...

    @abstractmethod
    async def update_form_field(self, form_field: UpdateFormField) -> FormField: ...

    @abstractmethod
    async def delete_form_field(self, form_field: DeleteFormField) -> FormField: ...

    @abstractmethod
    async def create_answer(self, answer: CreateAnswer) -> Answer: ...

    @abstractmethod
    async def read_answer(self, answer: ReadAnswer) -> Answer: ...

    @abstractmethod
    async def update_answer(self, answer: UpdateAnswer) -> Answer: ...

    @abstractmethod
    async def delete_answer(self, answer: DeleteAnswer) -> Answer: ...
