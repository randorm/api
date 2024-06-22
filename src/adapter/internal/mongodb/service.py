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

        model: models.Allocation = models.AllocationResolver.validate_python(allocation)

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

        return domain.AllocationResolver.validate_python(document)

    async def update_allocation(
        self,
        allocation: proto.UpdateAllocation,
    ) -> domain.Allocation:
        document: models.Allocation | None = await models.AllocationDocument.get(
            allocation.id,
            with_children=True,
        )  # type: ignore
        if document is None:
            raise  # todo: raise exception

        document = self.__update_allocation(document, allocation)
        document.updated_at = datetime.now()
        document = await document.update()

        return domain.AllocationResolver.validate_python(document)

    def __update_allocation(
        self, document: models.Allocation, source: proto.UpdateAllocation
    ):
        # todo: reflect type for compatibility
        if source.name is not None:
            document.name = source.name

        if source.due is not None:
            document.due = source.due

        if source.state is not None:
            document.state = source.state  # type: ignore

        if source.field_ids is not None:
            document.field_ids = source.field_ids

        if source.editor_ids is not None:
            document.editor_ids = source.editor_ids

        if source.participant_ids is not None:
            document.participant_ids = source.participant_ids  # type: ignore

        return document

    async def delete_allocation(
        self,
        allocation: proto.DeleteAllocation,
    ) -> domain.Allocation:
        document: models.Allocation | None = await models.AllocationDocument.get(
            allocation.id,
            with_children=True,
        )  # type: ignore
        if document is None:
            raise  # todo: raise exception

        document.deleted_at = datetime.now()
        document = await document.update()

        return domain.AllocationResolver.validate_python(document)

    async def create_form_field(
        self,
        form_field: proto.CreateFormField,
    ) -> domain.FormField:

        timestamp = datetime.now()
        form_field.created_at = timestamp
        form_field.updated_at = timestamp

        model: models.FormField = models.FormFieldResolver.validate_python(form_field)

        document = await model.insert()
        if document is None:
            raise  # todo: raise exception

        return domain.FormFieldResolver.validate_python(document)

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

        return domain.FormFieldResolver.validate_python(document)

    async def update_form_field(
        self,
        form_field: proto.UpdateFormField,
    ) -> domain.FormField:
        document: models.FormField | None = await models.FormFieldDocument.get(
            form_field.id,
            with_children=True,
        )  # type: ignore

        if document is None:
            raise  # todo: raise exception

        if isinstance(form_field, proto.UpdateTextFormField):
            if not isinstance(document, models.TextFormField):
                raise  # todo: raise exception

            document = self.__update_text_form_field(document, form_field)
        elif isinstance(form_field, proto.UpdateChoiceFormField):
            if not isinstance(document, models.ChoiceFormField):
                raise  # todo: raise exception

            document = self.__update_choice_form_field(document, form_field)
        document.updated_at = datetime.now()
        document = await document.update()

        return domain.FormatEntityResolver.validate_python(document)

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
        document: models.FormField | None = await models.FormFieldDocument.get(
            form_field.id,
            with_children=True,
        )  # type: ignore

        if document is None:
            raise  # todo: raise exception

        document.updated_at = datetime.now()
        document = await document.update()

        return domain.FormFieldResolver.validate_python(document)

    async def create_answer(
        self,
        answer: proto.CreateAnswer,
    ) -> domain.Answer:
        timestamp = datetime.now()
        answer.created_at = timestamp
        answer.updated_at = timestamp

        model = models.AnswerResolver.validate_python(answer)
        document = await model.insert()
        if document is None:
            raise  # todo: raise exception

        return domain.AnswerResolver.validate_python(document)

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

        return domain.AnswerResolver.validate_python(document)

    async def update_answer(
        self,
        answer: proto.UpdateAnswer,
    ) -> domain.Answer:
        document: models.Answer | None = await models.AnswerDocument.get(
            answer.id,
            with_children=True,
        )  # type: ignore

        if document is None:
            raise  # todo: raise exception

        if isinstance(answer, proto.UpdateTextAnswer):
            if not isinstance(document, models.TextAnswer):
                raise  # todo: raise exception

            document = self.__update_text_answer(document, answer)
        elif isinstance(answer, proto.UpdateChoiseAnswer):
            if not isinstance(document, models.ChoiceAnswer):
                raise  # todo: raise exception

            document = self.__update_choice_answer(document, answer)

        document.updated_at = datetime.now()
        document = await document.update()

        return domain.AnswerResolver.validate_python(document)

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
        document: models.Answer | None = await models.AnswerDocument.get(
            answer.id,
            with_children=True,
        )  # type: ignore
        if document is None:
            raise  # todo: raise exception

        document.deleted_at = datetime.now()
        document = await document.update()

        return domain.AnswerResolver.validate_python(document)

    async def create_user(
        self,
        user: proto.CreateUser,
    ) -> domain.User:
        timestamp = datetime.now()
        user.created_at = timestamp
        user.updated_at = timestamp

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
        document.updated_at = datetime.now()
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

        document.deleted_at = datetime.now()
        document = await document.update()

        return domain.User.model_validate(document, from_attributes=True)

    async def create_room(
        self,
        room: proto.CreateRoom,
    ) -> domain.Room:
        timestamp = datetime.now()
        room.created_at = timestamp
        room.updated_at = timestamp

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
        document.updated_at = datetime.now()
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

        document.deleted_at = datetime.now()
        document = await document.update()

        return domain.Room.model_validate(document, from_attributes=True)
