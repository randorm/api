import json
from datetime import datetime

from pydantic import BaseModel, ValidationError

import src.domain.exception.database as exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.domain.model.allocation import AllocationState
from src.domain.model.scalar.object_id import ObjectID


class MemoryDBAdapter(
    proto.AllocationDatabaseProtocol,
    proto.FormFieldDatabaseProtocol,
    proto.RoomDatabaseProtocol,
    proto.UserDatabaseProtocol,
    proto.ParticipantDatabaseProtocol,
    proto.PreferenceDatabaseProtocol,
):
    _allocation_collection: dict[ObjectID, domain.Allocation]
    _form_field_collection: dict[ObjectID, domain.FormField]
    _answer_collection: dict[ObjectID, domain.Answer]
    _user_collection: dict[ObjectID, domain.User]
    _room_collection: dict[ObjectID, domain.Room]
    _participant_collection: dict[ObjectID, domain.Participant]
    _preference_collection: dict[ObjectID, domain.Preference]

    def __init__(self):
        self._allocation_collection = {}
        self._form_field_collection = {}
        self._answer_collection = {}
        self._user_collection = {}
        self._room_collection = {}
        self._participant_collection = {}
        self._preference_collection = {}

    async def create_allocation(
        self,
        allocation: proto.CreateAllocation,
    ) -> domain.Allocation:
        try:
            timestamp = datetime.now().replace(microsecond=0)

            if not isinstance(allocation, BaseModel):
                raise TypeError("allocation must be a pydantic model")

            data = json.loads(allocation.model_dump_json())
            data["_id"] = str(ObjectID())
            data["created_at"] = timestamp
            data["updated_at"] = timestamp

            model: domain.Allocation = domain.AllocationResolver.validate_python(data)

            self._allocation_collection[model.id] = model
            document = self._allocation_collection.get(model.id)
            assert document is not None, "insert failed"

            return domain.AllocationResolver.validate_python(document)
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
            if not isinstance(allocation, BaseModel):
                raise TypeError("allocation must be a pydantic model")

            document = self._allocation_collection.get(allocation.id)
            assert document is not None, "document not found"

            return domain.AllocationResolver.validate_python(document)

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
            if not isinstance(allocation, BaseModel):
                raise TypeError("allocation must be a pydantic model")

            document = self._allocation_collection.get(allocation.id)
            assert document is not None, "document not found"

            document = self.__update_allocation(document, allocation)
            self._allocation_collection[allocation.id] = document
            document = self._allocation_collection.get(allocation.id)

            return domain.AllocationResolver.validate_python(document)

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
        self, document: domain.Allocation, source: proto.UpdateAllocation
    ):
        if source.name is not None:
            document.name = source.name

        if source.due is not None:
            document.due = source.due

        match source.state:
            case None:
                ...

            case AllocationState.CREATING | AllocationState.FAILED:
                document.state = source.state  # type: ignore
                document = domain.AllocationResolver.validate_python(
                    document.model_dump(by_alias=True)
                )

            case (
                AllocationState.CREATED
                | AllocationState.OPEN
                | AllocationState.ROOMING
                | AllocationState.ROOMED
                | AllocationState.CLOSED
            ):
                document.state = source.state  # type: ignore

                data = document.model_dump(by_alias=True)
                data["participants_ids"] = set()
                document = domain.AllocationResolver.validate_python(
                    data, from_attributes=True
                )

        if source.form_fields_ids is not None:
            document.form_fields_ids = source.form_fields_ids

        if source.editors_ids is not None:
            document.editors_ids = source.editors_ids

        if source.participants_ids is not None:
            if document.state not in [
                AllocationState.CREATED,
                AllocationState.OPEN,
                AllocationState.ROOMING,
                AllocationState.ROOMED,
                AllocationState.CLOSED,
            ]:
                raise exception.UpdateAllocationException(
                    f"can not change participant ids for document type {type(document)}"
                )
            document.participants_ids = source.participants_ids  # type: ignore

        return document

    async def delete_allocation(
        self,
        allocation: proto.DeleteAllocation,
    ) -> domain.Allocation:
        try:
            if not isinstance(allocation, BaseModel):
                raise TypeError("allocation must be a pydantic model")

            document = self._allocation_collection.get(allocation.id)
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            self._allocation_collection[allocation.id] = document

            return domain.AllocationResolver.validate_python(document)

        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAlloctionException(
                f"failed to reflect allocation type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteAllocationException(
                f"failed to delete allocation with id {allocation.id} with error: {e}"
            ) from e

    async def create_form_field(
        self,
        form_field: proto.CreateFormField,
    ) -> domain.FormField:
        try:
            if not isinstance(form_field, BaseModel):
                raise TypeError("form_field must be a pydantic model")

            timestamp = datetime.now().replace(microsecond=0)

            # todo: https://github.com/pydantic/pydantic/issues/4186
            data = json.loads(form_field.model_dump_json())
            data["_id"] = ObjectID()
            data["created_at"] = timestamp
            data["updated_at"] = timestamp

            model: domain.FormField = domain.FormFieldResolver.validate_python(data)

            self._form_field_collection[model.id] = model
            document = self._form_field_collection.get(model.id)
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
            if not isinstance(form_field, BaseModel):
                raise AttributeError("form_field must be a pydantic model")

            document = self._form_field_collection.get(form_field.id)
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
            if not isinstance(form_field, BaseModel):
                raise AttributeError("form_field must be a pydantic model")

            document = self._form_field_collection.get(form_field.id)
            assert document is not None, "document not found"

            if isinstance(form_field, proto.UpdateTextFormField):
                assert isinstance(
                    document, domain.TextFormField
                ), "can not change form field type"

                document = self.__update_text_form_field(document, form_field)
            elif isinstance(form_field, proto.UpdateChoiceFormField):
                assert isinstance(
                    document, domain.ChoiceFormField
                ), "can not change form field type"

                document = self.__update_choice_form_field(document, form_field)

            document.updated_at = datetime.now().replace(microsecond=0)

            self._form_field_collection[document.id] = document
            document = self._form_field_collection.get(document.id)

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
        document: domain.FormField,
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
        document: domain.TextFormField,
        source: proto.UpdateTextFormField,
    ) -> domain.TextFormField:
        self.__update_form_field(document, source)

        if source.re is not None:
            document.re = source.re

        if source.ex is not None:
            document.ex = source.ex

        return document

    def __update_choice_form_field(
        self,
        document: domain.ChoiceFormField,
        source: proto.UpdateChoiceFormField,
    ) -> domain.ChoiceFormField:
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

    async def delete_form_field(
        self,
        form_field: proto.DeleteFormField,
    ) -> domain.FormField:
        try:
            if not isinstance(form_field, BaseModel):
                raise AttributeError("form_field must be a pydantic model")

            document = self._form_field_collection.get(form_field.id)
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            self._form_field_collection[form_field.id] = document
            document = self._form_field_collection.get(form_field.id)

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
            if not isinstance(answer, BaseModel):
                raise TypeError("answer must be a pydantic model")

            timestamp = datetime.now().replace(microsecond=0)
            data = json.loads(answer.model_dump_json())
            data["_id"] = str(ObjectID())
            data["created_at"] = timestamp
            data["updated_at"] = timestamp

            model = domain.AnswerResolver.validate_python(data)
            self._answer_collection[model.id] = model
            document = self._answer_collection.get(model.id)
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
            if not isinstance(answer, BaseModel):
                raise AttributeError("answer must be a pydantic model")

            document = self._answer_collection.get(answer.id)
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
            if not isinstance(answer, BaseModel):
                raise AttributeError("answer must be a pydantic model")

            document = self._answer_collection.get(answer.id)
            assert document is not None, "document not found"

            if isinstance(answer, proto.UpdateTextAnswer):
                assert isinstance(
                    document, domain.TextAnswer
                ), "can not change answer type"

                document = self.__update_text_answer(document, answer)
            elif isinstance(answer, proto.UpdateChoiceAnswer):
                assert isinstance(
                    document, domain.ChoiceAnswer
                ), "can not change answer type"

                document = self.__update_choice_answer(document, answer)

            document.updated_at = datetime.now().replace(microsecond=0)
            self._answer_collection[answer.id] = document
            document = self._answer_collection.get(answer.id)

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
        document: domain.TextAnswer,
        source: proto.UpdateTextAnswer,
    ) -> domain.TextAnswer:
        if source.text is not None:
            document.text = source.text

        if source.text_entities is not None:
            document.text_entities = source.text_entities

        if source.field_id is not None:
            document.field_id = source.field_id

        return document

    def __update_choice_answer(
        self,
        document: domain.ChoiceAnswer,
        source: proto.UpdateChoiceAnswer,
    ) -> domain.ChoiceAnswer:
        if source.option_indexes is not None:
            document.option_indexes = source.option_indexes

        if source.field_id is not None:
            document.field_id = source.field_id

        return document

    async def delete_answer(
        self,
        answer: proto.DeleteAnswer,
    ) -> domain.Answer:
        try:
            if not isinstance(answer, BaseModel):
                raise AttributeError("answer must be a pydantic model")

            document = self._answer_collection.get(answer.id)
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            self._answer_collection[answer.id] = document
            document = self._answer_collection.get(answer.id)

            return domain.AnswerResolver.validate_python(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectAnswerException(
                f"failed to reflect answer type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteAnswerException(
                f"failed to delete answer with id {answer.id} with error: {e}"
            ) from e

    async def create_user(
        self,
        user: proto.CreateUser,
    ) -> domain.User:
        try:
            if not isinstance(user, BaseModel):
                raise TypeError("user must be a pydantic model")

            timestamp = datetime.now().replace(microsecond=0)

            data = json.loads(user.model_dump_json())
            data["_id"] = str(ObjectID())
            data["created_at"] = timestamp
            data["updated_at"] = timestamp

            model = domain.User.model_validate(data)

            self._user_collection[model.id] = model
            document = self._user_collection.get(model.id)

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
                    documents = [
                        item
                        for item in self._user_collection.values()
                        if user.telegram_id == item.telegram_id
                    ]

                case proto.FindUsersByProfileUsername():
                    documents = [
                        user
                        for user in self._user_collection.values()
                        if user.profile.username == user.profile.username
                    ]

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
            if not isinstance(user, BaseModel):
                raise AttributeError("user must be a pydantic model")

            document = self._user_collection.get(user.id)
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
            if not isinstance(user, BaseModel):
                raise AttributeError("user must be a pydantic model")

            document = self._user_collection.get(user.id)
            assert document is not None, "document not found"

            document = self.__update_user(document, user)
            document.updated_at = datetime.now().replace(microsecond=0)
            self._user_collection[user.id] = document
            document = self._user_collection.get(user.id)

            return domain.User.model_validate(document, from_attributes=True)

        except exception.UpdateUserException as e:
            raise e
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectUserException(
                f"failed to reflect user type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.UpdateUserException(
                f"failed to update user with id {user.id} with error: {e}"
            ) from e

    def __update_user(
        self,
        document: domain.User,
        source: proto.UpdateUser,
    ) -> domain.User:
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
            if not isinstance(user, BaseModel):
                raise AttributeError("user must be a pydantic model")

            document = self._user_collection.get(user.id)
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            self._user_collection[user.id] = document
            document = self._user_collection.get(user.id)

            return domain.User.model_validate(document, from_attributes=True)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectUserException(
                f"failed to reflect user type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteUserException(
                f"failed to delete user with id {user.id} with error: {e}"
            ) from e

    async def create_room(
        self,
        room: proto.CreateRoom,
    ) -> domain.Room:
        try:
            if not isinstance(room, BaseModel):
                raise TypeError("room must be a pydantic model")

            timestamp = datetime.now().replace(microsecond=0)

            data = json.loads(room.model_dump_json())
            data["_id"] = ObjectID()
            data["created_at"] = timestamp
            data["updated_at"] = timestamp

            model = domain.Room.model_validate(data, from_attributes=True)

            self._room_collection[model.id] = model
            document = self._room_collection.get(model.id)

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
            if not isinstance(room, BaseModel):
                raise AttributeError("room must be a pydantic model")

            document = self._room_collection.get(room.id)
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
            if not isinstance(room, BaseModel):
                raise AttributeError("room must be a pydantic model")

            document = self._room_collection.get(room.id)
            assert document is not None, "document not found"

            document = self.__update_room(document, room)
            document.updated_at = datetime.now().replace(microsecond=0)
            self._room_collection[room.id] = document
            document = self._room_collection.get(room.id)

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
        document: domain.Room,
        source: proto.UpdateRoom,
    ) -> domain.Room:
        if source.name is not None:
            document.name = source.name

        if source.capacity is not None:
            document.capacity = source.capacity

        if source.occupied is not None:
            document.occupied_ids = source.occupied

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
            if not isinstance(room, BaseModel):
                raise AttributeError("room must be a pydantic model")

            document = self._room_collection.get(room.id)
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            self._room_collection[room.id] = document
            document = self._room_collection.get(room.id)

            return domain.Room.model_validate(document, from_attributes=True)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectRoomException(
                f"failed to reflect room type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteRoomException(
                f"failed to delete room with id {room.id} with error: {e}"
            ) from e

    async def create_participant(
        self, participant: proto.CreateParticipant
    ) -> domain.Participant:
        try:
            if not isinstance(participant, BaseModel):
                raise TypeError("participant must be a pydantic model")

            timestamp = datetime.now().replace(microsecond=0)

            data = json.loads(participant.model_dump_json())
            data["_id"] = ObjectID()
            data["created_at"] = timestamp
            data["updated_at"] = timestamp

            model = domain.ParticipantResolver.validate_python(data)

            self._participant_collection[model.id] = model
            document = self._participant_collection.get(model.id)

            assert document is not None, "insert failed"

            return domain.ParticipantResolver.validate_python(document)
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
            if not isinstance(participant, BaseModel):
                raise AttributeError("participant must be a pydantic model")

            document = self._participant_collection.get(participant.id)
            assert document is not None, "document not found"

            return domain.ParticipantResolver.validate_python(document)
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
            if not isinstance(participant, BaseModel):
                raise AttributeError("participant must be a pydantic model")

            document = self._participant_collection.get(participant.id)
            assert document is not None, "document not found"

            document = self.__update_participant(document, participant)
            self._participant_collection[participant.id] = document
            document = self._participant_collection.get(participant.id)

            return domain.ParticipantResolver.validate_python(
                document, from_attributes=True
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
        document: domain.Participant,
        source: proto.UpdateParticipant,
    ) -> domain.Participant:
        if source.viewed_ids is not None:
            document.viewed_ids = source.viewed_ids

        if source.subscription_ids is not None:
            document.subscription_ids = source.subscription_ids

        if source.subscribers_ids is not None:
            document.subscribers_ids = source.subscribers_ids

        if source.state is not None:
            data = document.model_dump(by_alias=True)
            data["state"] = source.state
            document = domain.ParticipantResolver.validate_python(data)

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
            if not isinstance(participant, BaseModel):
                raise AttributeError("participant must be a pydantic model")

            document = self._participant_collection.get(participant.id)
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            self._participant_collection[participant.id] = document
            document = self._participant_collection.get(participant.id)

            return domain.ParticipantResolver.validate_python(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectParticipantException(
                f"failed to reflect participant type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeleteParticipantException(
                f"failed to delete participant with id {participant.id} with error: {e}"
            ) from e

    async def create_preference(
        self,
        preference: proto.CreatePreference,
    ) -> domain.Preference:
        try:
            if not isinstance(preference, BaseModel):
                raise TypeError("preference must be a pydantic model")

            timestamp = datetime.now().replace(microsecond=0)

            data = json.loads(preference.model_dump_json())
            data["_id"] = str(ObjectID())
            data["created_at"] = timestamp
            data["updated_at"] = timestamp

            model = domain.Preference.model_validate(data)

            self._preference_collection[model.id] = model
            document = self._preference_collection.get(model.id)

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

    async def read_preference(
        self,
        preference: proto.ReadPreference,
    ) -> domain.Preference:
        try:
            if not isinstance(preference, BaseModel):
                raise AttributeError("preference must be a pydantic model")

            document = self._preference_collection.get(preference.id)
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
        self,
        preference: proto.UpdatePreference,
    ) -> domain.Preference:
        try:
            if not isinstance(preference, BaseModel):
                raise AttributeError("preference must be a pydantic model")

            document = self._preference_collection.get(preference.id)
            assert document is not None, "document not found"

            document = self.__update_preference(document, preference)
            self._preference_collection[preference.id] = document
            document = self._preference_collection.get(preference.id)

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
        document: domain.Preference,
        source: proto.UpdatePreference,
    ) -> domain.Preference:
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
            if not isinstance(preference, BaseModel):
                raise AttributeError("preference must be a pydantic model")

            document = self._preference_collection.get(preference.id)
            assert document is not None, "document not found"

            document.deleted_at = datetime.now().replace(microsecond=0)
            self._preference_collection[preference.id] = document
            document = self._preference_collection.get(preference.id)

            return domain.Preference.model_validate(document)
        except (ValidationError, AttributeError) as e:
            raise exception.ReflectPreferenceException(
                f"failed to reflect preference type with error: {e}"
            ) from e
        except Exception as e:
            raise exception.DeletePreferenceException(
                f"failed to delete preference with id {preference.id} with error: {e}"
            ) from e
