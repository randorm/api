import beanie as bn
from pydantic import ConfigDict, TypeAdapter

import src.domain.model as domain


class User(bn.Document, domain.User):
    class Settings:
        indexes = ["id", "tid"]
        name = "users"


class Room(bn.Document, domain.Room):
    class Settings:
        indexes = ["id"]
        name = "rooms"


class FormFieldDocument(bn.Document):
    class Settings:
        indexes = ["id"]
        name = "form_fields"
        is_root = True


class TextFormField(FormFieldDocument, domain.TextFormField): ...


class ChoiceFormField(FormFieldDocument, domain.ChoiceField): ...


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
