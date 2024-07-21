import asyncio

import beanie as bn
from icecream import ic
from motor.motor_asyncio import AsyncIOMotorClient
from polyfactory.factories.beanie_odm_factory import BeanieDocumentFactory as Factory

import src.domain.model as domain
from src.adapter.internal.database import mongodb

N_USERS = 500
N_ALLOCATIONS = 1
N_FORM_FIELDS = 10
N_ANSWERS = N_ALLOCATIONS * N_FORM_FIELDS * 2


async def main():  # noqa: C901
    client = AsyncIOMotorClient("mongodb://localhost:27017")

    await client.drop_database("randorm")

    await bn.init_beanie(
        client.randorm,
        document_models=[
            mongodb.models.ActiveParticipant,
            mongodb.models.AllocatedParticipant,
            mongodb.models.AllocationDocument,
            mongodb.models.AnswerDocument,
            mongodb.models.ChoiceAnswer,
            mongodb.models.ChoiceFormField,
            mongodb.models.ClosedAllocation,
            mongodb.models.CreatedAllocation,
            mongodb.models.CreatedParticipant,
            mongodb.models.CreatingAllocation,
            mongodb.models.CreatingParticipant,
            mongodb.models.FailedAllocation,
            mongodb.models.FormFieldDocument,
            mongodb.models.OpenAllocation,
            mongodb.models.ParticipantDocument,
            mongodb.models.Preference,
            mongodb.models.Room,
            mongodb.models.RoomedAllocation,
            mongodb.models.RoomingAllocation,
            mongodb.models.TextAnswer,
            mongodb.models.TextFormField,
            mongodb.models.User,
        ],
    )

    class UserF(Factory[mongodb.models.User]): ...

    users = await asyncio.gather(*[UserF.build().insert() for _ in range(N_USERS)])
    ic(len(users))

    class TextFormFieldF(Factory[mongodb.models.TextFormField]):
        re = None

        @classmethod
        def editors_ids(cls) -> set[domain.ObjectID]:
            return {  # type: ignore
                x.id
                for x in cls.__random__.choices(users, k=cls.__random__.randint(2, 5))
            }

        @classmethod
        def creator_id(cls) -> domain.ObjectID:
            return cls.__random__.choice(users).id  # type: ignore

    class ChoiceFormFieldF(Factory[mongodb.models.ChoiceFormField]):
        @classmethod
        def editors_ids(cls) -> set[domain.ObjectID]:
            return {  # type: ignore
                x.id
                for x in cls.__random__.choices(users, k=cls.__random__.randint(2, 5))
            }

        @classmethod
        def creator_id(cls) -> domain.ObjectID:
            return cls.__random__.choice(users).id  # type: ignore

    text_form_fields = await asyncio.gather(
        *[TextFormFieldF.build().insert() for _ in range(N_FORM_FIELDS)]
    )
    ic(len(text_form_fields))

    choice_form_fields = await asyncio.gather(
        *[ChoiceFormFieldF.build().insert() for _ in range(N_FORM_FIELDS)]
    )
    ic(len(choice_form_fields))

    class AllocationF(Factory[mongodb.models.OpenAllocation]):
        @classmethod
        def form_fields_ids(cls) -> set[domain.ObjectID]:
            _text = {
                x.id
                for x in cls.__random__.choices(
                    text_form_fields, k=cls.__random__.randint(1, 15)
                )
            }
            _choice = {
                x.id
                for x in cls.__random__.choices(choice_form_fields, k=15 - len(_text))
            }

            return _text | _choice

        @classmethod
        def editors_ids(cls) -> set[domain.ObjectID]:
            return {
                x.id
                for x in cls.__random__.choices(users, k=cls.__random__.randint(2, 5))
            }

        @classmethod
        def creator_id(cls) -> domain.ObjectID:
            return cls.__random__.choice(users).id

    allocations = await asyncio.gather(
        *[AllocationF.build().insert() for _ in range(N_ALLOCATIONS)]
    )
    ic(len(allocations))

    class ParticipantF(Factory[mongodb.models.CreatingParticipant]):
        @classmethod
        def allocation_id(cls) -> domain.ObjectID:
            return cls.__random__.choice(allocations).id

    participants = []
    for user in users:
        participant = ParticipantF.build()
        participant.user_id = user.id
        participants.append(participant)

    participants = await asyncio.gather(
        *[participant.insert() for participant in participants]
    )

    ic(len(participants))

    class AnswerF(Factory[mongodb.models.TextAnswer]):
        @classmethod
        def respondent_id(cls) -> domain.ObjectID:
            return cls.__random__.choice(participants).id

        @classmethod
        def form_field_id(cls) -> domain.ObjectID:
            return cls.__random__.choice(text_form_fields).id

    class ChoiceAnswerF(Factory[mongodb.models.ChoiceAnswer]):
        @classmethod
        def respondent_id(cls) -> domain.ObjectID:
            return cls.__random__.choice(participants).id

        @classmethod
        def form_field_id(cls) -> domain.ObjectID:
            return cls.__random__.choice(choice_form_fields).id

        @classmethod
        def option_indexes(cls) -> list[int]:
            return [cls.__random__.choice(list(range(5)))]

    answers = await asyncio.gather(
        *[AnswerF.build().insert() for _ in range(N_ANSWERS)]
    )
    ic(len(answers))
