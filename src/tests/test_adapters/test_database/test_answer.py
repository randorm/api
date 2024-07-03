from collections.abc import Awaitable, Callable

import pytest
from pydantic import BaseModel, ConfigDict

import src.domain.exception.database as exception
import src.domain.model as domain
import src.protocol.internal.database.form_field as proto
from src.adapter.internal.memorydb.service import MemoryDBAdapter
from src.adapter.internal.mongodb.service import MongoDBAdapter


async def _get_mongo():
    return await MongoDBAdapter.create("mongodb://localhost:27017")


async def _get_memory():
    return MemoryDBAdapter()


type ActorFn = Callable[[], Awaitable[proto.FormFieldDatabaseProtocol]]

param_string = "actor_fn"
param_attrs = [_get_mongo, _get_memory]


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_text_answer_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    field_id = domain.ObjectID()

    data = proto.CreateTextAnswer(
        text="test",
        text_entities={domain.BoldEntity(offset=0, length=4)},
        field_id=field_id,
        respondent_id=owner,
    )

    response = await actor.create_answer(data)

    assert response.kind == domain.FormFieldKind.TEXT
    assert isinstance(response, domain.TextAnswer)
    assert response.respondent_id == owner
    assert response.field_id == field_id
    assert response.text == data.text
    assert response.text_entities == data.text_entities
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_choise_answer_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    field_id = domain.ObjectID()

    data = proto.CreateChoiceAnswer(
        option_ids={domain.ObjectID()},
        field_id=field_id,
        respondent_id=owner,
    )

    response = await actor.create_answer(data)

    assert response.kind == domain.FormFieldKind.CHOICE
    assert isinstance(response, domain.ChoiceAnswer)
    assert response.respondent_id == owner
    assert response.field_id == field_id
    assert response.option_ids == data.option_ids
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_text_answer_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    field_id = domain.ObjectID()

    data = proto.CreateTextAnswer(
        text="test",
        text_entities={domain.BoldEntity(offset=0, length=4)},
        field_id=field_id,
        respondent_id=owner,
    )

    document = await actor.create_answer(data)

    response = await actor.read_answer(proto.ReadAnswer(_id=document.id))

    assert response.kind == domain.FormFieldKind.TEXT
    assert isinstance(response, domain.TextAnswer)
    assert response.respondent_id == owner
    assert response.field_id == field_id
    assert response.text == data.text
    assert response.text_entities == data.text_entities
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_choice_answer_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    field_id = domain.ObjectID()

    data = proto.CreateChoiceAnswer(
        option_ids={domain.ObjectID()},
        field_id=field_id,
        respondent_id=owner,
    )

    document = await actor.create_answer(data)

    response = await actor.read_answer(proto.ReadAnswer(_id=document.id))

    assert response.kind == domain.FormFieldKind.CHOICE
    assert isinstance(response, domain.ChoiceAnswer)
    assert response.respondent_id == owner
    assert response.field_id == field_id
    assert response.option_ids == data.option_ids
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_text_answer_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    field_id = domain.ObjectID()

    data = proto.CreateTextAnswer(
        text="test",
        text_entities={domain.BoldEntity(offset=0, length=4)},
        field_id=field_id,
        respondent_id=owner,
    )

    document = await actor.create_answer(data)

    new_data = proto.UpdateTextAnswer(
        _id=document.id,
        text="test2",
        text_entities={domain.ItalicEntity(offset=0, length=4)},
    )

    response = await actor.update_answer(new_data)

    assert response.kind == domain.FormFieldKind.TEXT
    assert isinstance(response, domain.TextAnswer)
    assert response.respondent_id == owner
    assert response.field_id == field_id
    assert response.text == new_data.text
    assert response.text_entities == new_data.text_entities
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_choice_answer_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    field_id = domain.ObjectID()

    data = proto.CreateChoiceAnswer(
        option_ids={domain.ObjectID()},
        field_id=field_id,
        respondent_id=owner,
    )

    document = await actor.create_answer(data)

    new_data = proto.UpdateChoiceAnswer(
        _id=document.id,
        option_ids={domain.ObjectID(), domain.ObjectID(), domain.ObjectID()},
    )

    response = await actor.update_answer(new_data)

    assert response.kind == domain.FormFieldKind.CHOICE
    assert isinstance(response, domain.ChoiceAnswer)
    assert response.respondent_id == owner
    assert response.field_id == field_id
    assert response.option_ids == new_data.option_ids
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_text_answer_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    field_id = domain.ObjectID()

    data = proto.CreateTextAnswer(
        text="test",
        text_entities={domain.BoldEntity(offset=0, length=4)},
        field_id=field_id,
        respondent_id=owner,
    )

    document = await actor.create_answer(data)

    response = await actor.delete_answer(proto.DeleteAnswer(_id=document.id))

    assert response.kind == domain.FormFieldKind.TEXT
    assert isinstance(response, domain.TextAnswer)
    assert response.respondent_id == owner
    assert response.field_id == field_id
    assert response.text == data.text
    assert response.text_entities == data.text_entities
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is not None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_choice_answer_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    field_id = domain.ObjectID()

    data = proto.CreateChoiceAnswer(
        option_ids={domain.ObjectID()},
        field_id=field_id,
        respondent_id=owner,
    )

    document = await actor.create_answer(data)

    response = await actor.delete_answer(proto.DeleteAnswer(_id=document.id))

    assert response.kind == domain.FormFieldKind.CHOICE
    assert isinstance(response, domain.ChoiceAnswer)
    assert response.respondent_id == owner
    assert response.field_id == field_id
    assert response.option_ids == data.option_ids
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is not None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_text_answer_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateAnswerException):
        await actor.create_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_choice_answer_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateAnswerException):
        await actor.create_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_text_answer_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectAnswerException):
        await actor.read_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_choice_answer_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectAnswerException):
        await actor.read_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_text_answer_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectAnswerException):
        await actor.update_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_choice_answer_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectAnswerException):
        await actor.update_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_text_answer_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectAnswerException):
        await actor.delete_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_choice_answer_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectAnswerException):
        await actor.delete_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_text_answer_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadAnswerException):
        await actor.read_answer(proto.ReadAnswer(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_choice_answer_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadAnswerException):
        await actor.read_answer(proto.ReadAnswer(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_text_answer_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateAnswerException):
        await actor.update_answer(proto.UpdateTextAnswer(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_choice_answer_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateAnswerException):
        await actor.update_answer(proto.UpdateChoiceAnswer(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_text_answer_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteAnswerException):
        await actor.delete_answer(proto.DeleteAnswer(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_choice_answer_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteAnswerException):
        await actor.delete_answer(proto.DeleteAnswer(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_text_answer_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAnswerException):
        await actor.create_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_choice_answer_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAnswerException):
        await actor.create_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_text_answer_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAnswerException):
        await actor.read_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_choice_answer_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAnswerException):
        await actor.read_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_text_answer_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAnswerException):
        await actor.update_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_choice_answer_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAnswerException):
        await actor.update_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_text_answer_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAnswerException):
        await actor.delete_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_choice_answer_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAnswerException):
        await actor.delete_answer(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_text_answer_field_id_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateTextAnswer(
        text="test",
        text_entities={domain.BoldEntity(offset=0, length=4)},
        field_id=domain.ObjectID(),
        respondent_id=owner,
    )

    document = await actor.create_answer(data)

    new_field_id = domain.ObjectID()

    new_data = proto.UpdateTextAnswer(
        _id=document.id,
        text="test2",
        text_entities={domain.ItalicEntity(offset=0, length=4)},
        field_id=new_field_id,
    )

    response = await actor.update_answer(new_data)

    assert response.kind == domain.FormFieldKind.TEXT
    assert isinstance(response, domain.TextAnswer)
    assert response.respondent_id == owner
    assert response.field_id == new_field_id
    assert response.text == new_data.text
    assert response.text_entities == new_data.text_entities
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_choice_answer_field_id_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateChoiceAnswer(
        option_ids={domain.ObjectID()},
        field_id=domain.ObjectID(),
        respondent_id=owner,
    )

    document = await actor.create_answer(data)

    new_field_id = domain.ObjectID()

    new_data = proto.UpdateChoiceAnswer(
        _id=document.id,
        option_ids={domain.ObjectID(), domain.ObjectID(), domain.ObjectID()},
        field_id=new_field_id,
    )

    response = await actor.update_answer(new_data)

    assert response.kind == domain.FormFieldKind.CHOICE
    assert isinstance(response, domain.ChoiceAnswer)
    assert response.respondent_id == owner
    assert response.field_id == new_field_id
    assert response.option_ids == new_data.option_ids
    assert response.created_at is not None
    assert response.updated_at is not None
    assert response.deleted_at is None
