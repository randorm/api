from datetime import datetime
from typing import Any

import beanie as bn
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import ValidationError

import src.domain.exception.database as exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.adapter.internal.database.mongodb import models
from src.domain.model.allocation import AllocationState


class MongoDBAdapter(
    proto.AllocationDatabaseProtocol,
    proto.FormFieldDatabaseProtocol,
    proto.ParticipantDatabaseProtocol,
    proto.RoomDatabaseProtocol,
    proto.UserDatabaseProtocol,
    proto.PreferenceDatabaseProtocol,
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
                models.ActiveParticipant,
                models.AllocatedParticipant,
                models.AllocationDocument,
                models.AnswerDocument,
                models.ChoiceAnswer,
                models.ChoiceFormField,
                models.ClosedAllocation,
                models.CreatedAllocation,
                models.CreatedParticipant,
                models.CreatingAllocation,
                models.CreatingParticipant,
                models.FailedAllocation,
                models.FormFieldDocument,
                models.OpenAllocation,
                models.ParticipantDocument,
                models.Preference,
                models.Room,
                models.RoomedAllocation,
                models.RoomingAllocation,
                models.TextAnswer,
                models.TextFormField,
                models.User,
            ],
        )

        return self

    async def create_allocation(
        self,
        allocation: proto.CreateAllocation,
    ) -> domain.Allocation:
        try:
            timestamp = datetime.now().replace(microsecond=0)
            allocation.created_at = timestamp
            allocation.updated_at = timestamp

            model: models.Allocation = models.AllocationResolver.validate_python(
                allocation,
                from_attributes=True,
            )

            document: models.Allocation = await model.insert()
            assert document is not None, "insert failed"

            return domain.AllocationResolver.validate_python(
                document.model_dump(by_alias=True)
            )
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAlloctionException(
                f"failed to reflect allocation type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.CreateAllocationException(
                f"failed to save allocation to database with error: {e}"
            ) from e

    async def read_allocation(
        self,
        allocation: proto.ReadAllocation,
    ) -> domain.Allocation:
        try:
            document = await models.AllocationDocument.get(
                allocation.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            return domain.AllocationResolver.validate_python(
                document.model_dump(by_alias=True)
            )

        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAlloctionException(
                f"failed to reflect allocation type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadAllocationException(
                f"failed to fetch allocation with id {allocation.id} with error: {e}"
            ) from e

    async def update_allocation(
        self,
        allocation: proto.UpdateAllocation,
    ) -> domain.Allocation:
        try:
            document: models.Allocation | None = await models.AllocationDocument.get(
                allocation.id,
                with_children=True,
            )  # type: ignore
            assert document is not None, "document not found"

            document = self.__update_allocation(document, allocation)
            document.updated_at = datetime.now().replace(microsecond=0)

            # todo: replace with new `.replace` call
            # todo: tracking issue https://github.com/BeanieODM/beanie/issues/955
            await models.AllocationDocument.find_one(
                models.AllocationDocument.id == document.id,
                with_children=True,
            ).replace_one(document)
            await document.sync()

            return domain.AllocationResolver.validate_python(
                document.model_dump(by_alias=True)
            )

        except exception.UpdateAllocationException as e:
            raise e
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAlloctionException(
                f"failed to reflect allocation type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.UpdateAllocationException(
                f"failed to update allocation with id {allocation.id} with error: {e}"
            ) from e

    def __update_allocation(
        self, document: models.Allocation, source: proto.UpdateAllocation
    ) -> models.Allocation:
        data = document.model_dump(by_alias=True)

        if source.name is not None:
            data["name"] = source.name

        if source.due is not None:
            data["due"] = source.due

        match source.state:
            case None:
                ...

            case AllocationState.CREATING | AllocationState.FAILED:
                data["state"] = source.state
                del data["participants_ids"]

            case (
                AllocationState.CREATED
                | AllocationState.OPEN
                | AllocationState.ROOMING
                | AllocationState.ROOMED
                | AllocationState.CLOSED
            ):
                data["state"] = source.state
                data["participants_ids"] = set()

        if source.form_fields_ids is not None:
            data["form_fields_ids"] = source.form_fields_ids

        if source.editors_ids is not None:
            data["editors_ids"] = source.editors_ids

        if source.participants_ids is not None:
            if data["state"] not in [
                AllocationState.CREATED,
                AllocationState.OPEN,
                AllocationState.ROOMING,
                AllocationState.ROOMED,
                AllocationState.CLOSED,
            ]:
                raise exception.UpdateAllocationException(
                    f"can not change participant ids for document state {data['state']}"
                )

            data["participants_ids"] = source.participants_ids

        return models.AllocationResolver.validate_python(data, from_attributes=True)

    async def delete_allocation(
        self,
        allocation: proto.DeleteAllocation,
    ) -> domain.Allocation:
        try:
            document: models.Allocation | None = await models.AllocationDocument.get(
                allocation.id,
                with_children=True,
            )  # type: ignore
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            document = await document.replace()
            assert document is not None, "document replacement failed"

            return domain.AllocationResolver.validate_python(
                document.model_dump(by_alias=True)
            )

        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAlloctionException(
                f"failed to reflect allocation type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteAllocationException(
                f"failed to delete allocation with id {allocation.id} with error: {e}"
            ) from e

    async def read_many_allocations(
        self,
        allocations: list[proto.ReadAllocation],
    ) -> list[domain.Allocation | None]:
        ids = [allocation.id for allocation in allocations]
        try:
            documents = await models.AllocationDocument.find_many(
                {"_id": {"$in": ids}},
                with_children=True,
            ).to_list()

            aligned = {document.id: document for document in documents}

            return [
                (
                    domain.AllocationResolver.validate_python(document)
                    if (document := aligned.get(id)) is not None
                    else None
                )
                for id in ids
            ]
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAlloctionException(
                f"failed to reflect allocation type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadAllocationException(
                f"failed to read allocations with ids {ids} with error: {e}"
            ) from e

    async def create_form_field(
        self,
        form_field: proto.CreateFormField,
    ) -> domain.FormField:
        try:
            timestamp = datetime.now().replace(microsecond=0)
            form_field.created_at = timestamp
            form_field.updated_at = timestamp

            model: models.FormField = models.FormFieldResolver.validate_python(
                form_field, from_attributes=True
            )

            document = await model.insert()
            assert document is not None, "insert failed"

            return domain.FormFieldResolver.validate_python(document)

        except (ValidationError, AttributeError) as e:
            raise exception.ReflectFormFieldException(
                f"failed to reflect form field type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.CreateFormFieldException(
                f"failed to create form field with error: {e}"
            ) from e

    async def read_form_field(
        self,
        form_field: proto.ReadFormField,
    ) -> domain.FormField:
        try:
            document = await models.FormFieldDocument.get(
                form_field.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            return domain.FormFieldResolver.validate_python(document)

        except (ValidationError, AttributeError) as e:
            raise exception.ReflectFormFieldException(
                f"failed to reflect form field type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadFormFieldException(
                f"failed to read form field with id {form_field.id} with error: {e}"
            ) from e

    async def update_form_field(
        self,
        form_field: proto.UpdateFormField,
    ) -> domain.FormField:
        try:
            document: models.FormField | None = await models.FormFieldDocument.get(
                form_field.id,
                with_children=True,
            )  # type: ignore
            assert document is not None, "document not found"

            if isinstance(form_field, proto.UpdateTextFormField):
                assert isinstance(
                    document, models.TextFormField
                ), "can not change form field type"

                document = self.__update_text_form_field(document, form_field)
            elif isinstance(form_field, proto.UpdateChoiceFormField):
                assert isinstance(
                    document, models.ChoiceFormField
                ), "can not change form field type"

                document = self.__update_choice_form_field(document, form_field)

            document.updated_at = datetime.now().replace(microsecond=0)
            await models.FormFieldDocument.find_one(
                models.FormFieldDocument.id == document.id,
                with_children=True,
            ).replace_one(document)
            await document.sync()

            return domain.FormFieldResolver.validate_python(
                document, from_attributes=True
            )

        except exception.UpdateFormFieldException as e:
            raise e
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectFormFieldException(
                f"failed to reflect form field type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.UpdateFormFieldException(
                f"failed to update form field with id {form_field.id} with error: {e}"
            ) from e

    def __update_form_field(
        self,
        document: models.FormField,
        source: proto.UpdateFormField,
    ):
        if source.required is not None:
            document.required = source.required

        if source.frozen is not None:
            document.frozen = source.frozen

        if source.question is not None:
            document.question = source.question

        if source.question_entities is not None:
            document.question_entities = source.question_entities

        if source.respondent_count is not None:
            document.respondent_count = source.respondent_count

        if source.editors_ids is not None:
            document.editors_ids = source.editors_ids

    def __update_text_form_field(
        self,
        document: models.TextFormField,
        source: proto.UpdateTextFormField,
    ) -> models.TextFormField:
        self.__update_form_field(document, source)

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
        self.__update_form_field(document, source)

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

    async def read_many_form_fields(
        self,
        form_fields: list[proto.ReadFormField],
    ) -> list[domain.FormField | None]:
        ids = [form_field.id for form_field in form_fields]
        try:
            documents = await models.FormFieldDocument.find_many(
                {"_id": {"$in": ids}},
                with_children=True,
            ).to_list()

            aligned = {document.id: document for document in documents}

            return [
                (
                    domain.FormFieldResolver.validate_python(document)
                    if (document := aligned.get(id)) is not None
                    else None
                )
                for id in ids
            ]
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectFormFieldException(
                f"failed to reflect form field type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadFormFieldException(
                f"failed to read form fields with ids {ids} with error: {e}"
            ) from e

    async def delete_form_field(
        self,
        form_field: proto.DeleteFormField,
    ) -> domain.FormField:
        try:
            document: models.FormField | None = await models.FormFieldDocument.get(
                form_field.id,
                with_children=True,
            )  # type: ignore
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            document = await document.replace()

            return domain.FormFieldResolver.validate_python(document)

        except (ValidationError, AttributeError) as e:
            raise exception.ReflectFormFieldException(
                f"failed to reflect form field type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteFormFieldException(
                f"failed to delete form field with id {form_field.id} with error: {e}"
            ) from e

    async def create_answer(
        self,
        answer: proto.CreateAnswer,
    ) -> domain.Answer:
        try:
            timestamp = datetime.now().replace(microsecond=0)
            answer.created_at = timestamp
            answer.updated_at = timestamp

            model = models.AnswerResolver.validate_python(
                answer,
                from_attributes=True,
            )
            document = await model.insert()
            assert document is not None, "insert failed"

            return domain.AnswerResolver.validate_python(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAnswerException(
                f"failed to reflect answer type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.CreateAnswerException(
                f"failed to create answer with error: {e}"
            ) from e

    async def read_answer(
        self,
        answer: proto.ReadAnswer,
    ) -> domain.Answer:
        try:
            document = await models.AnswerDocument.get(
                answer.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            return domain.AnswerResolver.validate_python(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAnswerException(
                f"failed to reflect answer type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadAnswerException(
                f"failed to read answer with id {answer.id} with error: {e}"
            ) from e

    async def update_answer(
        self,
        answer: proto.UpdateAnswer,
    ) -> domain.Answer:
        try:
            document: models.Answer | None = await models.AnswerDocument.get(
                answer.id,
                with_children=True,
            )  # type: ignore

            assert document is not None, "document not found"

            if isinstance(answer, proto.UpdateTextAnswer):
                assert isinstance(
                    document, models.TextAnswer
                ), "can not change answer type"

                document = self.__update_text_answer(document, answer)
            elif isinstance(answer, proto.UpdateChoiceAnswer):
                assert isinstance(
                    document, models.ChoiceAnswer
                ), "can not change answer type"

                document = self.__update_choice_answer(document, answer)

            document.updated_at = datetime.now().replace(microsecond=0)
            document = await document.replace()

            return domain.AnswerResolver.validate_python(document)

        except exception.UpdateAnswerException as e:
            raise e
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAnswerException(
                f"failed to reflect answer type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.UpdateAnswerException(
                f"failed to update answer with id {answer.id} with error: {e}"
            ) from e

    def __update_text_answer(
        self,
        document: models.TextAnswer,
        source: proto.UpdateTextAnswer,
    ) -> models.TextAnswer:
        if source.text is not None:
            document.text = source.text

        if source.text_entities is not None:
            document.text_entities = source.text_entities

        return document

    def __update_choice_answer(
        self,
        document: models.ChoiceAnswer,
        source: proto.UpdateChoiceAnswer,
    ) -> models.ChoiceAnswer:
        if source.option_indexes is not None:
            document.option_indexes = source.option_indexes

        return document

    async def delete_answer(
        self,
        answer: proto.DeleteAnswer,
    ) -> domain.Answer:
        try:
            document: models.Answer | None = await models.AnswerDocument.get(
                answer.id,
                with_children=True,
            )  # type: ignore
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            document = await document.replace()

            return domain.AnswerResolver.validate_python(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAnswerException(
                f"failed to reflect answer type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteAnswerException(
                f"failed to delete answer with id {answer.id} with error: {e}"
            ) from e

    async def read_many_answers(
        self,
        answers: list[proto.ReadAnswer],
    ) -> list[domain.Answer | None]:
        ids = [answer.id for answer in answers]
        try:
            documents = await models.AnswerDocument.find_many(
                {"_id": {"$in": ids}},
                with_children=True,
            ).to_list()

            aligned = {document.id: document for document in documents}

            return [
                (
                    domain.AnswerResolver.validate_python(document)
                    if (document := aligned.get(id)) is not None
                    else None
                )
                for id in ids
            ]
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAnswerException(
                f"failed to reflect answer type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadAnswerException(
                f"failed to read answers with ids {ids} with error: {e}"
            ) from e

    async def create_user(
        self,
        user: proto.CreateUser,
    ) -> domain.User:
        try:
            timestamp = datetime.now().replace(microsecond=0)
            user.created_at = timestamp
            user.updated_at = timestamp

            model = models.User.model_validate(user, from_attributes=True)
            document = await model.insert()
            assert document is not None, "insert failed"

            return domain.User.model_validate(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectUserException(
                f"failed to reflect user type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.CreateUserException(
                f"failed to create user with error: {e}"
            ) from e

    async def find_users(self, user: proto.FindUsers) -> list[domain.User]:
        try:
            match user:
                case proto.FindUsersByTid():
                    documents = await models.User.find_many(
                        {"telegram_id": user.telegram_id}
                    ).to_list()

                case proto.FindUsersByProfileUsername():
                    documents = await models.User.find_many(
                        {"profile.username": user.username}
                    ).to_list()

                case _:
                    documents = []

            return [domain.User.model_validate(document) for document in documents]

        except (ValidationError, AttributeError) as e:
            raise exception.ReflectUserException(
                f"failed to reflect user type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.FindUsersException(
                f"failed to find users with error: {e}"
            ) from e

    async def read_user(
        self,
        user: proto.ReadUser,
    ) -> domain.User:
        try:
            document = await models.User.get(
                user.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            return domain.User.model_validate(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectUserException(
                f"failed to reflect user type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadUserException(
                f"failed to read user with id {user.id} with error: {e}"
            ) from e

    async def update_user(
        self,
        user: proto.UpdateUser,
    ) -> domain.User:
        try:
            document = await models.User.get(
                user.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            document = self.__update_user(document, user)
            document.updated_at = datetime.now().replace(microsecond=0)
            document = await document.replace()

            return domain.User.model_validate(document, from_attributes=True)

        except exception.UpdateUserException as e:
            raise e
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectUserException(
                "failed to reflect user type with error: ", e
            ) from e
        except Exception as e:
            raise exception.UpdateUserException(
                f"failed to update user with id {user.id} with error: ", e
            ) from e

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
        try:
            document = await models.User.get(
                user.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            document = await document.replace()

            return domain.User.model_validate(document, from_attributes=True)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectUserException(
                f"failed to reflect user type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteUserException(
                f"failed to delete user with id {user.id} with error: {e}"
            ) from e

    async def read_many_users(
        self,
        users: list[proto.ReadUser],
    ) -> list[domain.User | None]:
        ids = [user.id for user in users]
        try:
            documents = await models.User.find_many(
                {"_id": {"$in": ids}},
                with_children=True,
            ).to_list()

            aligned = {document.id: document for document in documents}

            return [
                (
                    domain.User.model_validate(document)
                    if (document := aligned.get(id)) is not None
                    else None
                )
                for id in ids
            ]
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectUserException(
                f"failed to reflect user type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadUserException(
                f"failed to read users with ids {ids} with error: {e}"
            ) from e

    async def create_room(
        self,
        room: proto.CreateRoom,
    ) -> domain.Room:
        try:
            timestamp = datetime.now().replace(microsecond=0)
            room.created_at = timestamp
            room.updated_at = timestamp

            model = models.Room.model_validate(room, from_attributes=True)
            document = await model.insert()
            assert document is not None, "insert failed"

            return domain.Room.model_validate(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectRoomException(
                f"failed to reflect room type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.CreateRoomException(
                f"failed to create room with error: {e}"
            ) from e

    async def read_room(
        self,
        room: proto.ReadRoom,
    ) -> domain.Room:
        try:
            document = await models.Room.get(
                room.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            return domain.Room.model_validate(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectRoomException(
                f"failed to reflect room type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadRoomException(
                f"failed to read room with id {room.id} with error: {e}"
            ) from e

    async def update_room(
        self,
        room: proto.UpdateRoom,
    ) -> domain.Room:
        try:
            document = await models.Room.get(
                room.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            document = self.__update_room(document, room)
            document.updated_at = datetime.now().replace(microsecond=0)
            document = await document.replace()

            return domain.Room.model_validate(document, from_attributes=True)
        except exception.UpdateRoomException as e:
            raise e
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectRoomException(
                f"failed to reflect room type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.UpdateRoomException(
                f"failed to update room with id {room.id} with error: {e}"
            ) from e

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

        if source.editors_ids is not None:
            document.editors_ids = source.editors_ids

        return document

    async def delete_room(
        self,
        room: proto.DeleteRoom,
    ) -> domain.Room:
        try:
            document = await models.Room.get(
                room.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            document = await document.replace()

            return domain.Room.model_validate(document, from_attributes=True)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectRoomException(
                f"failed to reflect room type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteRoomException(
                f"failed to delete room with id {room.id} with error: {e}"
            ) from e

    async def read_many_rooms(
        self,
        rooms: list[proto.ReadRoom],
    ) -> list[domain.Room | None]:
        ids = [room.id for room in rooms]
        try:
            documents = await models.Room.find_many(
                {"_id": {"$in": ids}},
                with_children=True,
            ).to_list()

            aligned = {document.id: document for document in documents}

            return [
                (
                    domain.Room.model_validate(document)
                    if (document := aligned.get(id)) is not None
                    else None
                )
                for id in ids
            ]
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectRoomException(
                f"failed to reflect room type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadRoomException(
                f"failed to read rooms with ids {ids} with error: {e}"
            ) from e

    async def create_participant(
        self, participant: proto.CreateParticipant
    ) -> domain.Participant:
        try:
            timestamp = datetime.now().replace(microsecond=0)
            participant.created_at = timestamp
            participant.updated_at = timestamp

            model = models.ParticipantResolver.validate_python(
                participant,
                from_attributes=True,
            )
            document = await model.insert()
            assert document is not None, "insert failed"

            return domain.ParticipantResolver.validate_python(
                document.model_dump(by_alias=True),
                from_attributes=True,
            )
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectParticipantException(
                f"failed to reflect participant type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.CreateParticipantException(
                f"failed to create participant with error: {e}"
            ) from e

    async def read_participant(
        self, participant: proto.ReadParticipant
    ) -> domain.Participant:
        try:
            document = await models.ParticipantDocument.get(
                participant.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            return domain.ParticipantResolver.validate_python(
                document.model_dump(by_alias=True),
                from_attributes=True,
            )
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectParticipantException(
                f"failed to reflect participant type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadParticipantException(
                f"failed to read participant with id {participant.id} with error: {e}"
            ) from e

    async def update_participant(
        self, participant: proto.UpdateParticipant
    ) -> domain.Participant:
        try:
            document: models.Participant | None = await models.ParticipantDocument.get(
                participant.id,
                with_children=True,
            )  # type: ignore
            assert document is not None, "document not found"

            document = self.__update_participant(document, participant)
            document.updated_at = datetime.now().replace(microsecond=0)
            await models.ParticipantDocument.find_one(
                models.ParticipantDocument.id == document.id,
                with_children=True,
            ).replace_one(document)
            await document.sync()

            return domain.ParticipantResolver.validate_python(
                document.model_dump(by_alias=True),
                from_attributes=True,
            )
        except exception.UpdateParticipantException as e:
            raise e
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectParticipantException(
                f"failed to reflect participant type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.UpdateParticipantException(
                f"failed to update participant with id {participant.id} with error: {e}"
            ) from e

    def __update_participant(
        self,
        document: models.Participant,
        source: proto.UpdateParticipant,
    ) -> models.Participant:
        if source.viewed_ids is not None:
            document.viewed_ids = source.viewed_ids

        if source.subscription_ids is not None:
            document.subscription_ids = source.subscription_ids

        if source.subscribers_ids is not None:
            document.subscribers_ids = source.subscribers_ids

        if source.state is not None:
            data = document.model_dump(by_alias=True)
            data["state"] = source.state
            document = models.ParticipantResolver.validate_python(data)

        if source.room_id is not None:
            if document.state not in [domain.ParticipantState.ALLOCATED]:
                raise exception.UpdateParticipantException(
                    f"can not change room id for participant state {document.state}"
                )

            document.room_id = source.room_id  # type: ignore

        return document

    async def delete_participant(
        self, participant: proto.DeleteParticipant
    ) -> domain.Participant:
        try:
            document: models.Participant | None = await models.ParticipantDocument.get(
                participant.id,
                with_children=True,
            )  # type: ignore
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            document = await document.replace()
            assert document is not None, "document replacement failed"

            return domain.ParticipantResolver.validate_python(
                document.model_dump(by_alias=True),
                from_attributes=True,
            )
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectParticipantException(
                f"failed to reflect participant type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteParticipantException(
                f"failed to delete participant with id {participant.id} with error: {e}"
            ) from e

    async def read_many_participants(
        self,
        participants: list[proto.ReadParticipant],
    ) -> list[domain.Participant | None]:
        ids = [participant.id for participant in participants]
        try:
            documents = await models.ParticipantDocument.find_many(
                {"_id": {"$in": ids}},
                with_children=True,
            ).to_list()

            aligned = {document.id: document for document in documents}

            return [
                (
                    domain.ParticipantResolver.validate_python(document)
                    if (document := aligned.get(id)) is not None
                    else None
                )
                for id in ids
            ]
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectParticipantException(
                f"failed to reflect participant type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadParticipantException(
                f"failed to read participants with ids {ids} with error: {e}"
            ) from e

    async def create_preference(
        self, preference: proto.CreatePreference
    ) -> domain.Preference:
        try:
            timestamp = datetime.now().replace(microsecond=0)
            preference.created_at = timestamp
            preference.updated_at = timestamp

            model = models.Preference.model_validate(preference, from_attributes=True)
            document = await model.insert()
            assert document is not None, "insert failed"

            return domain.Preference.model_validate(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectPreferenceException(
                f"failed to reflect preference type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.CreatePreferenceException(
                f"failed to create preference with error: {e}"
            ) from e

    async def find_preferences(
        self, preference: proto.FindPreference
    ) -> list[domain.Preference]:
        try:
            documents = await models.Preference.find_many(
                {"user_id": preference.user_id, "target_id": preference.target_id}
            ).to_list()

            return [
                domain.Preference.model_validate(document) for document in documents
            ]
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectPreferenceException(
                f"failed to reflect preference type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.FindPreferenceException(
                f"failed to find preferences with error: {e}"
            ) from e

    async def read_preference(
        self, preference: proto.ReadPreference
    ) -> domain.Preference:
        try:
            document = await models.Preference.get(
                preference.id,
                with_children=True,
            )
            assert document is not None, "document not found"

            return domain.Preference.model_validate(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectPreferenceException(
                f"failed to reflect preference type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadPreferenceException(
                f"failed to read preference with id {preference.id} with error: {e}"
            ) from e

    async def update_preference(
        self, preference: proto.UpdatePreference
    ) -> domain.Preference:
        try:
            document: models.Preference | None = await models.Preference.get(
                preference.id
            )
            assert document is not None, "document not found"

            document = self.__update_preference(document, preference)
            document.updated_at = datetime.now().replace(microsecond=0)
            await models.Preference.find_one(
                models.Preference.id == document.id,
                with_children=True,
            ).replace_one(document)
            await document.sync()

            return domain.Preference.model_validate(document)
        except exception.UpdatePreferenceException as e:
            raise e
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectPreferenceException(
                f"failed to reflect preference type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.UpdatePreferenceException(
                f"failed to update preference with id {preference.id} with error: {e}"
            ) from e

    def __update_preference(
        self,
        document: models.Preference,
        source: proto.UpdatePreference,
    ) -> models.Preference:
        if source.kind is not None:
            document.kind = source.kind

        if source.status is not None:
            document.status = source.status

        return document

    async def delete_preference(
        self,
        preference: proto.DeletePreference,
    ) -> domain.Preference:
        try:
            document: models.Preference | None = await models.Preference.get(
                preference.id
            )
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            document = await document.replace()
            assert document is not None, "document replacement failed"

            return domain.Preference.model_validate(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectPreferenceException(
                f"failed to reflect preference type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeletePreferenceException(
                f"failed to delete preference with id {preference.id} with error: {e}"
            ) from e

    async def read_many_preferences(
        self,
        preferences: list[proto.ReadPreference],
    ) -> list[domain.Preference | None]:
        ids = [preference.id for preference in preferences]
        try:
            documents = await models.Preference.find_many(
                {"_id": {"$in": ids}},
                with_children=True,
            ).to_list()

            aligned = {document.id: document for document in documents}

            return [
                (
                    domain.Preference.model_validate(document)
                    if (document := aligned.get(id)) is not None
                    else None
                )
                for id in ids
            ]
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectPreferenceException(
                f"failed to reflect preference type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.ReadPreferenceException(
                f"failed to read preferences with ids {ids} with error: {e}"
            ) from e
