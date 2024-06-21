from datetime import datetime
from typing import Any

import beanie as bn
from motor.motor_asyncio import AsyncIOMotorClient

import src.domain.model as domain
import src.protocol.internal.database as proto
from src.adapter.internal.mongodb import models


class MongoDBAdapter(
    proto.AllocationDatabaseProtocol,
    proto.FormFieldDatabaseProtocol,
    proto.RoomDatabaseProtocol,
    proto.UserDatabaseProtocol,
):
    _client: AsyncIOMotorClient

    def __init__(self):
        pass

    @classmethod
    async def create(cls, dsn: str, **client_args: Any):
        self = cls()
        self._client = AsyncIOMotorClient(dsn, **client_args)

        await bn.init_beanie(
            self._client.db_name,
            document_models=[
                models.User,
                models.Room,
                models.FormFieldDocument,
                models.AnswerDocument,
                models.AllocationDocument,
            ],
        )

        return self

    async def create_allocation(
        self,
        allocation: proto.CreateAllocation,
    ) -> domain.Allocation:

        timestamp = datetime.now()
        allocation.created_at = timestamp
        allocation.updated_at = timestamp

        model: models.Allocation = models.AllocationResolver.validate_python(
            allocation,
            from_attributes=True,
        )

        document: models.Allocation = await model.insert()
        if document is None:
            raise  # todo: raise exception

        return domain.AllocationResolver.validate_python(document)

    async def read_allocation(
        self,
        allocation: proto.ReadAllocation,
    ) -> domain.Allocation:
        document = await models.AllocationDocument.get(
            allocation.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        match document:
            case models.CreatedAllocation():
                reflected_type = domain.CreatingAllocation

            case models.CreatingAllocation():
                reflected_type = domain.CreatingAllocation

            case models.CreatedAllocation():
                reflected_type = domain.CreatedAllocation

            case models.OpenAllocation():
                reflected_type = domain.OpenAllocation

            case models.RoomingAllocation():
                reflected_type = domain.RoomingAllocation

            case models.RoomedAllocation():
                reflected_type = domain.RoomedAllocation

            case models.ClosedAllocation():
                reflected_type = domain.ClosedAllocation

            case models.FailedAllocation():
                reflected_type = domain.FailedAllocation
            case _:
                raise  # todo: raise exception

        return reflected_type.model_validate(document)

    async def update_allocation(
        self,
        allocation: proto.UpdateAllocation,
    ) -> domain.Allocation:
        document = await models.AllocationDocument.get(
            allocation.id,
            with_children=True,
        )

        if document is None:
            raise  # todo: raise exception

        document = self.__update_allocation(document, allocation)

        document = await document.update()

        match document.state:
            case domain.AllocationState.CREATING:
                reflected_type = domain.CreatingAllocation

            case domain.AllocationState.CREATED:
                reflected_type = domain.CreatedAllocation

            case domain.AllocationState.OPEN:
                reflected_type = domain.OpenAllocation

            case domain.AllocationState.ROOMING:
                reflected_type = domain.RoomingAllocation

            case domain.AllocationState.ROOMED:
                reflected_type = domain.RoomedAllocation

            case domain.AllocationState.CLOSED:
                reflected_type = domain.ClosedAllocation

            case domain.AllocationState.FAILED:
                reflected_type = domain.FailedAllocation

            case _:
                raise  # todo: raise exception

        return reflected_type.model_validate(document, from_attributes=True)

    def __update_allocation(
        self, document: models.Allocation, source: proto.UpdateAllocation
    ):
        # todo: reflect type for compatibility
        if source.name is not None:
            document.name = source.name

        if source.due is not None:
            document.due = source.due

        if source.state is not None:
            document.state = source.state

        if source.field_ids is not None:
            document.field_ids = source.field_ids

        if source.editor_ids is not None:
            document.editor_ids = source.editor_ids

        if source.participant_ids is not None:
            document.participant_ids = source.participant_ids

        return document

    async def delete_allocation(
        self,
        allocation: proto.DeleteAllocation,
    ) -> domain.Allocation:
        document = await models.AllocationDocument.get(
            allocation.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        delete_result = await document.delete()
        if delete_result is None:
            raise  # todo: raise exception

        match document:
            case models.CreatingAllocation():
                reflected_type = domain.CreatingAllocation

            case models.CreatedAllocation():
                reflected_type = domain.CreatedAllocation

            case models.OpenAllocation():
                reflected_type = domain.OpenAllocation

            case models.RoomingAllocation():
                reflected_type = domain.RoomingAllocation

            case models.RoomedAllocation():
                reflected_type = domain.RoomedAllocation

            case models.ClosedAllocation():
                reflected_type = domain.ClosedAllocation

            case models.FailedAllocation():
                reflected_type = domain.FailedAllocation

            case _:
                raise  # todo: raise exception

        return reflected_type.model_validate(document, from_attributes=True)

    async def create_form_field(
        self,
        form_field: proto.CreateFormField,
    ) -> domain.FormField:
        match form_field:
            case proto.CreateTextFormField:
                reflected_type = models.TextFormField
                domain_reflected_type = domain.TextFormField

            case proto.CreateChoiceFormField:
                reflected_type = models.ChoiceFormField
                domain_reflected_type = domain.ChoiceField

            case _:
                raise  # todo: raise exception

        model = reflected_type.model_validate(form_field, from_attributes=True)
        document = await reflected_type.insert_one(model)
        if document is None:
            raise  # todo: raise exception

        return domain_reflected_type.model_validate(document)

    async def read_form_field(
        self,
        form_field: proto.ReadFormField,
    ) -> domain.FormField:
        document = await models.FormFieldDocument.get(
            form_field.id,
            with_children=True,
        )

        if document is None:
            raise  # todo: raise exception

        match document:
            case models.TextFormField():
                reflected_type = domain.TextFormField

            case models.ChoiceFormField():
                reflected_type = domain.ChoiceField

            case _:
                raise  # todo: raise exception

        return reflected_type.model_validate(document)

    async def update_form_field(
        self,
        form_field: proto.UpdateFormField,
    ) -> domain.FormField:
        document = await models.FormFieldDocument.get(
            form_field.id,
            with_children=True,
        )

        if document is None:
            raise  # todo: raise exception

        match form_field:
            case proto.UpdateTextFormField():
                if not isinstance(document, models.TextFormField):
                    raise  # todo: raise exception

                document = self.__update_text_form_field(document, form_field)
                reflected_type = domain.TextFormField
            case proto.UpdateChoiceFormField():
                if not isinstance(document, models.ChoiceFormField):
                    raise  # todo: raise exception

                document = self.__update_choice_form_field(document, form_field)
                reflected_type = domain.ChoiceField
            case _:
                raise  # todo: raise exception

        document = await document.update()

        return reflected_type.model_validate(document)

    def __update_text_form_field(
        self,
        document: models.TextFormField,
        source: proto.UpdateTextFormField,
    ) -> models.TextFormField:
        if source.required is not None:
            document.required = source.required

        if source.question is not None:
            document.question = source.question

        if source.question_entities is not None:
            document.question_entities = source.question_entities

        if source.respondent_count is not None:
            document.respondent_count = source.respondent_count

        if source.editor_ids is not None:
            document.editor_ids = source.editor_ids

        if source.re is not None:
            document.re = source.re

        if source.ex is not None:
            document.ex = source.ex

        return document

    def __update_choice_form_field(
        self,
        document: models.ChoiceFormField,
        source: proto.UpdateChoiceFormField,
    ) -> models.ChoiceFormField:
        if source.options is not None:
            for index, option in enumerate(source.options):
                if option is None:
                    continue

                if option.text is not None:
                    document.options[index].text = option.text

                if option.respondent_count is not None:
                    document.options[index].respondent_count = option.respondent_count

        if source.multiple is not None:
            document.multiple = source.multiple

        return document

    async def delete_form_field(
        self,
        form_field: proto.DeleteFormField,
    ) -> domain.FormField:
        document = await models.FormFieldDocument.get(
            form_field.id,
            with_children=True,
        )

        if document is None:
            raise  # todo: raise exception

        delete_result = await document.delete()

        if delete_result is None:
            raise  # todo: raise exception

        match document:
            case models.TextFormField():
                reflected_type = domain.TextFormField

            case models.ChoiceFormField():
                reflected_type = domain.ChoiceField

            case _:
                raise  # todo: raise exception

        return reflected_type.model_validate(document, from_attributes=True)

    async def create_answer(
        self,
        answer: proto.CreateAnswer,
    ) -> domain.Answer:
        match answer:
            case proto.CreateTextAnswer():
                reflected_type = models.TextAnswer
                domain_reflected_type = domain.TextAnswer

            case proto.CreateChoiseAnswer():
                reflected_type = models.ChoiceAnswer
                domain_reflected_type = domain.ChoiceAnswer

            case _:
                raise  # todo: raise exception

        model = reflected_type.model_validate(answer, from_attributes=True)
        document = await reflected_type.insert_one(model)
        if document is None:
            raise  # todo: raise exception

        return domain_reflected_type.model_validate(document)

    async def read_answer(
        self,
        answer: proto.ReadAnswer,
    ) -> domain.Answer:
        document = await models.AnswerDocument.get(
            answer.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        match document:
            case models.TextAnswer():
                reflected_type = domain.TextAnswer

            case models.ChoiceAnswer():
                reflected_type = domain.ChoiceAnswer

            case _:
                raise  # todo: raise exception

        return reflected_type.model_validate(document)

    async def update_answer(
        self,
        answer: proto.UpdateAnswer,
    ) -> domain.Answer:
        document = await models.AnswerDocument.get(
            answer.id,
            with_children=True,
        )

        if document is None:
            raise  # todo: raise exception

        match answer:
            case proto.UpdateTextAnswer():
                if not isinstance(document, models.TextAnswer):
                    raise  # todo: raise exception

                document = self.__update_text_answer(document, answer)
                reflected_type = domain.TextAnswer
            case proto.UpdateChoiseAnswer():
                if not isinstance(document, models.ChoiceAnswer):
                    raise  # todo: raise exception

                document = self.__update_choice_answer(document, answer)
                reflected_type = domain.ChoiceAnswer
            case _:
                raise  # todo: raise exception

        document = await document.update()

        return reflected_type.model_validate(document, from_attributes=True)

    def __update_text_answer(
        self,
        document: models.TextAnswer,
        source: proto.UpdateTextAnswer,
    ) -> models.TextAnswer:
        if source.text is not None:
            document.text = source.text

        if source.text_entities is not None:
            document.text_entities = source.text_entities

        if source.field_id is not None:
            document.field_id = source.field_id

        return document

    def __update_choice_answer(
        self,
        document: models.ChoiceAnswer,
        source: proto.UpdateChoiseAnswer,
    ) -> models.ChoiceAnswer:
        if source.option_ids is not None:
            document.option_ids = source.option_ids

        if source.field_id is not None:
            document.field_id = source.field_id

        return document

    async def delete_answer(
        self,
        answer: proto.DeleteAnswer,
    ) -> domain.Answer:
        document = await models.AnswerDocument.get(
            answer.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        delete_result = await document.delete()
        if delete_result is None:
            raise  # todo: raise exception

        match document:
            case models.TextAnswer():
                reflected_type = domain.TextAnswer

            case models.ChoiceAnswer():
                reflected_type = domain.ChoiceAnswer

            case _:
                raise  # todo: raise exception

        return reflected_type.model_validate(document, from_attributes=True)

    async def create_user(
        self,
        user: proto.CreateUser,
    ) -> domain.User:
        model = models.User.model_validate(user, from_attributes=True)
        document = await models.User.insert_one(model)
        if document is None:
            raise  # todo: raise exception

        return domain.User.model_validate(document)

    async def read_user(
        self,
        user: proto.ReadUser,
    ) -> domain.User:
        document = await models.User.get(
            user.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        return domain.User.model_validate(document)

    async def update_user(
        self,
        user: proto.UpdateUser,
    ) -> domain.User:
        document = await models.User.get(
            user.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        document = self.__update_user(document, user)

        document = await document.update()

        return domain.User.model_validate(document, from_attributes=True)

    def __update_user(
        self,
        document: models.User,
        source: proto.UpdateUser,
    ) -> models.User:
        if source.views is not None:
            document.views = source.views

        if source.profile is None:
            return document

        if source.profile.first_name is not None:
            document.profile.first_name = source.profile.first_name

        if source.profile.last_name is not None:
            document.profile.last_name = source.profile.last_name

        if source.profile.username is not None:
            document.profile.username = source.profile.username

        if source.profile.language_code is not None:
            document.profile.language_code = source.profile.language_code

        if source.profile.gender is not None:
            document.profile.gender = source.profile.gender

        if source.profile.birthdate is not None:
            document.profile.birthdate = source.profile.birthdate

        return document

    async def delete_user(
        self,
        user: proto.DeleteUser,
    ) -> domain.User:
        document = await models.User.get(
            user.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        delete_result = await document.delete()
        if delete_result is None:
            raise  # todo: raise exception

        return domain.User.model_validate(document, from_attributes=True)

    async def create_room(
        self,
        room: proto.CreateRoom,
    ) -> domain.Room:
        model = models.Room.model_validate(room, from_attributes=True)
        document = await models.Room.insert_one(model)
        if document is None:
            raise  # todo: raise exception

        return domain.Room.model_validate(document)

    async def read_room(
        self,
        room: proto.ReadRoom,
    ) -> domain.Room:
        document = await models.Room.get(
            room.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        return domain.Room.model_validate(document)

    async def update_room(
        self,
        room: proto.UpdateRoom,
    ) -> domain.Room:
        document = await models.Room.get(
            room.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        document = self.__update_room(document, room)

        document = await document.update()

        return domain.Room.model_validate(document, from_attributes=True)

    def __update_room(
        self,
        document: models.Room,
        source: proto.UpdateRoom,
    ) -> models.Room:
        if source.name is not None:
            document.name = source.name

        if source.capacity is not None:
            document.capacity = source.capacity

        if source.occupied is not None:
            document.occupied = source.occupied

        if source.gender_restriction is not None:
            document.gender_restriction = source.gender_restriction

        if source.editor_ids is not None:
            document.editor_ids = source.editor_ids

        return document

    async def delete_room(
        self,
        room: proto.DeleteRoom,
    ) -> domain.Room:
        document = await models.Room.get(
            room.id,
            with_children=True,
        )
        if document is None:
            raise  # todo: raise exception

        delete_result = await document.delete()
        if delete_result is None:
            raise  # todo: raise exception

        return domain.Room.model_validate(document, from_attributes=True)
