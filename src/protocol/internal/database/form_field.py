from abc import ABC, abstractmethod
from re import Pattern
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter

from src.domain.model.form_field import (
    Answer,
    ChoiceAnswer,
    ChoiceFormField,
    ChoiceOption,
    FormField,
    TextAnswer,
    TextFormField,
)
from src.domain.model.format_entity import FormatEntity
from src.domain.model.scalar.object_id import ObjectID
from src.protocol.internal.database.mixin import ExcludeFieldMixin


class CreateTextFormField(ExcludeFieldMixin, TextFormField): ...


class CreateChoiceFormField(ExcludeFieldMixin, ChoiceFormField): ...


type CreateFormField = CreateTextFormField | CreateChoiceFormField

CreateFormFieldResolver = TypeAdapter(
    type=CreateFormField,
    config=ConfigDict(extra="ignore", from_attributes=True),
)


class ReadFormField(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateTextFormField(ExcludeFieldMixin, TextFormField):
    id: ObjectID = Field(alias="_id")
    # optional fields
    required: bool | None = Field(default=None)
    frozen: bool | None = Field(default=None)
    question: str | None = Field(default=None)
    question_entities: set[FormatEntity] | None = Field(default=None)
    respondent_count: int | None = Field(default=None)
    editor_ids: set[ObjectID] | None = Field(default=None)
    re: Pattern[str] | None = Field(default=None)
    ex: str | None = Field(default=None)
    # exclude
    creator_id: Literal[None] = None
    allocation_id: Literal[None] = None


class UpdateChoiceOption(ChoiceOption):
    text: str | None = Field(default=None)
    respondent_count: int | None = Field(default=None)


class UpdateChoiceFormField(ExcludeFieldMixin, ChoiceFormField):
    id: ObjectID = Field(alias="_id")
    # optional fields
    required: bool | None = Field(default=None)
    frozen: bool | None = Field(default=None)
    question: str | None = Field(default=None)
    question_entities: set[FormatEntity] | None = Field(default=None)
    respondent_count: int | None = Field(default=None)
    editor_ids: set[ObjectID] | None = Field(default=None)
    options: list[UpdateChoiceOption | None] | None = Field(default=None)
    multiple: bool | None = Field(default=None)
    # exclude
    creator_id: Literal[None] = None
    allocation_id: Literal[None] = None


type UpdateFormField = UpdateTextFormField | UpdateChoiceFormField

UpdateFormFieldResolver = TypeAdapter(
    type=UpdateFormField,
    config=ConfigDict(extra="ignore", from_attributes=True),
)


class DeleteFormField(BaseModel):
    id: ObjectID = Field(alias="_id")


class CreateTextAnswer(ExcludeFieldMixin, TextAnswer): ...


class CreateChoiceAnswer(ExcludeFieldMixin, ChoiceAnswer): ...


type CreateAnswer = CreateTextAnswer | CreateChoiceAnswer


CreateAnswerResolver = TypeAdapter(
    type=CreateAnswer,
    config=ConfigDict(extra="ignore", from_attributes=True),
)


class ReadAnswer(BaseModel):
    id: ObjectID = Field(alias="_id")


class UpdateTextAnswer(ExcludeFieldMixin, TextAnswer):
    id: ObjectID = Field(alias="_id")
    text: str | None = Field(default=None)
    text_entities: set[FormatEntity] | None = Field(default=None)
    field_id: ObjectID | None = Field(default=None)
    # exclude
    respondent_id: Literal[None] = None


class UpdateChoiceAnswer(ExcludeFieldMixin, ChoiceAnswer):
    id: ObjectID = Field(alias="_id")
    option_indexes: set[int] | None = Field(default=None)
    field_id: ObjectID | None = Field(default=None)
    # exclude
    respondent_id: Literal[None] = None


type UpdateAnswer = UpdateTextAnswer | UpdateChoiceAnswer

UpdateAnswerResolver = TypeAdapter(
    type=UpdateAnswer,
    config=ConfigDict(extra="ignore", from_attributes=True),
)


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
