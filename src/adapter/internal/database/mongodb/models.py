import re
from typing import Any

import beanie as bn
import bson
from pydantic import ConfigDict, TypeAdapter, field_validator

import src.domain.model as domain


class User(bn.Document, domain.User):
    class Settings:
        indexes = ["id", "telegram_id"]
        name = "users"


class Room(bn.Document, domain.Room):
    class Settings:
        indexes = ["id"]
        name = "rooms"


class FormFieldDocument(bn.Document):
    class Settings:
        name = "form_fields"
        is_root = True


def re_pattern_to_bson_regex(pattern: re.Pattern) -> bson.Regex:
    regex = bson.Regex.from_native(pattern)
    regex.flags ^= re.UNICODE

    return regex


class TextFormField(FormFieldDocument, domain.TextFormField):
    class Settings:
        bson_encoders = {re.Pattern: re_pattern_to_bson_regex}

    @field_validator("re", mode="before")
    @classmethod
    def deserialize_re(cls, value: Any) -> re.Pattern | None:
        if value is None:
            return None

        if isinstance(value, str):
            return re.compile(value)

        if isinstance(value, re.Pattern):
            return value

        if isinstance(value, bson.Regex):
            return value.try_compile()

        raise TypeError(
            "re must be a string, a compiled regular expression, or a pymongo regex"
        )


class ChoiceFormField(FormFieldDocument, domain.ChoiceFormField): ...


type FormField = TextFormField | ChoiceFormField

FormFieldResolver = TypeAdapter(
    FormField,
    config=ConfigDict(extra="ignore", from_attributes=True),
)


class AnswerDocument(bn.Document):
    class Settings:
        indexes = ["id"]
        name = "answers"
        is_root = True


class TextAnswer(AnswerDocument, domain.TextAnswer): ...


class ChoiceAnswer(AnswerDocument, domain.ChoiceAnswer): ...


type Answer = TextAnswer | ChoiceAnswer

AnswerResolver = TypeAdapter(
    Answer,
    config=ConfigDict(extra="ignore", from_attributes=True),
)


class AllocationDocument(bn.Document):
    class Settings:
        name = "allocations"
        is_root = True


class CreatingAllocation(AllocationDocument, domain.CreatingAllocation): ...


class CreatedAllocation(AllocationDocument, domain.CreatedAllocation): ...


class OpenAllocation(AllocationDocument, domain.OpenAllocation): ...


class RoomingAllocation(AllocationDocument, domain.RoomingAllocation): ...


class RoomedAllocation(AllocationDocument, domain.RoomedAllocation): ...


class ClosedAllocation(AllocationDocument, domain.ClosedAllocation): ...


class FailedAllocation(AllocationDocument, domain.FailedAllocation): ...


type Allocation = (
    CreatingAllocation
    | CreatedAllocation
    | OpenAllocation
    | RoomingAllocation
    | RoomedAllocation
    | ClosedAllocation
    | FailedAllocation
)

AllocationResolver = TypeAdapter(
    Allocation,
    config=ConfigDict(extra="ignore", from_attributes=True),
)


class ParticipantDocument(bn.Document):
    class Settings:
        indexes = ["id"]
        name = "participants"
        is_root = True


class CreatingParticipant(ParticipantDocument, domain.CreatingParticipant): ...


class CreatedParticipant(ParticipantDocument, domain.CreatedParticipant): ...


class ActiveParticipant(ParticipantDocument, domain.ActiveParticipant): ...


class AllocatedParticipant(ParticipantDocument, domain.AllocatedParticipant): ...


type Participant = (
    CreatingParticipant | CreatedParticipant | ActiveParticipant | AllocatedParticipant
)

ParticipantResolver = TypeAdapter(
    Participant,
    config=ConfigDict(extra="ignore", from_attributes=True),
)


class Preference(bn.Document, domain.Preference):
    class Settings:
        indexes = ["id"]
        name = "preferences"
