import re
from collections.abc import Awaitable, Callable
from datetime import datetime

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
async def test_create_text_form_field_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateTextFormField(
        required=True,
        question="test",
        question_entities={domain.BoldEntity(offset=0, length=4)},
        creator_id=owner,
        editor_ids={owner},
        re=re.compile(r".+"),
        ex="test",
    )

    response = await actor.create_form_field(data)

    assert response.kind == domain.FormFieldKind.TEXT
    assert isinstance(response, domain.TextFormField)
    assert response.required == data.required
    assert response.question == data.question
    assert response.question_entities == data.question_entities
    assert response.respondent_count == 0
    assert response.creator_id == owner
    assert response.editor_ids == {owner}
    assert response.re == data.re
    assert response.ex == data.ex
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_choice_form_field_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateChoiceFormField(
        required=True,
        question="test",
        question_entities={domain.BoldEntity(offset=0, length=4)},
        creator_id=owner,
        editor_ids={owner},
        options=[
            domain.ChoiceOption(text="test1"),
            domain.ChoiceOption(text="test2"),
            domain.ChoiceOption(text="test3"),
        ],
        multiple=False,
    )

    response = await actor.create_form_field(data)

    assert response.kind == domain.FormFieldKind.CHOICE
    assert isinstance(response, domain.ChoiceField)
    assert response.required == data.required
    assert response.question == data.question
    assert response.question_entities == data.question_entities
    assert response.respondent_count == 0
    assert response.creator_id == owner
    assert response.editor_ids == {owner}
    assert len(response.options) == len(data.options)
    assert response.options == data.options
    assert response.multiple == data.multiple
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_text_form_field_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateTextFormField(
        required=True,
        question="test",
        question_entities={domain.BoldEntity(offset=0, length=4)},
        creator_id=owner,
        editor_ids={owner},
        re=re.compile(r".+"),
        ex="test",
    )

    document = await actor.create_form_field(data)

    response = await actor.read_form_field(proto.ReadFormField(_id=document.id))

    assert response.kind == domain.FormFieldKind.TEXT
    assert isinstance(response, domain.TextFormField)
    assert response.required == data.required
    assert response.question == data.question
    assert response.question_entities == data.question_entities
    assert response.respondent_count == 0
    assert response.creator_id == owner
    assert response.editor_ids == {owner}
    assert response.re == data.re
    assert response.ex == data.ex
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_choice_form_field_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateChoiceFormField(
        required=True,
        question="test",
        question_entities={domain.BoldEntity(offset=0, length=4)},
        creator_id=owner,
        editor_ids={owner},
        options=[
            domain.ChoiceOption(text="test1"),
            domain.ChoiceOption(text="test2"),
            domain.ChoiceOption(text="test3"),
        ],
        multiple=False,
    )

    document = await actor.create_form_field(data)

    response = await actor.read_form_field(proto.ReadFormField(_id=document.id))

    assert response.kind == domain.FormFieldKind.CHOICE
    assert isinstance(response, domain.ChoiceField)
    assert response.required == data.required
    assert response.question == data.question
    assert response.question_entities == data.question_entities
    assert response.respondent_count == 0
    assert response.creator_id == owner
    assert response.editor_ids == {owner}
    assert len(response.options) == len(data.options)
    assert response.options == data.options
    assert response.multiple == data.multiple
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_text_form_field_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateTextFormField(
        required=True,
        question="test",
        question_entities={domain.BoldEntity(offset=0, length=4)},
        creator_id=owner,
        editor_ids={owner},
        respondent_count=0,
        re=re.compile(r".+"),
        ex="test",
    )

    document = await actor.create_form_field(data)
    new_editors = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}

    new_data = proto.UpdateTextFormField(
        _id=document.id,
        required=False,
        question="test2",
        question_entities={domain.ItalicEntity(offset=0, length=4)},
        re=re.compile(r".*"),
        ex="test2",
        respondent_count=1000,
        editor_ids=new_editors,
    )

    response = await actor.update_form_field(new_data)

    assert response.kind == domain.FormFieldKind.TEXT
    assert isinstance(response, domain.TextFormField)
    assert response.required == new_data.required
    assert response.question == new_data.question
    assert response.question_entities == new_data.question_entities
    assert response.respondent_count == 1000
    assert response.creator_id == owner
    assert response.editor_ids == new_editors
    assert response.re == new_data.re
    assert response.ex == new_data.ex
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_choice_form_field_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateChoiceFormField(
        required=True,
        question="test",
        question_entities={domain.BoldEntity(offset=0, length=4)},
        creator_id=owner,
        editor_ids={owner},
        options=[
            domain.ChoiceOption(text="test1"),
            domain.ChoiceOption(text="test2"),
            domain.ChoiceOption(text="test3"),
        ],
        multiple=False,
    )

    document = await actor.create_form_field(data)
    new_editors = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}

    new_data = proto.UpdateChoiceFormField(
        _id=document.id,
        required=False,
        question="test2-2",
        question_entities={domain.ItalicEntity(offset=0, length=4)},
        options=[
            None,
            proto.UpdateChoiceOption(text="test2-2"),
            proto.UpdateChoiceOption(respondent_count=1000),
        ],
        multiple=False,
        editor_ids=new_editors,
    )

    response = await actor.update_form_field(new_data)

    assert response.kind == domain.FormFieldKind.CHOICE
    assert isinstance(response, domain.ChoiceField)
    assert response.required == new_data.required
    assert response.question == new_data.question
    assert response.question_entities == new_data.question_entities
    assert response.respondent_count == 0
    assert response.creator_id == owner
    assert response.editor_ids == new_editors
    assert len(response.options) == 3
    assert response.options[0].text == "test1"
    assert response.options[0].respondent_count == 0
    assert response.options[1].text == "test2-2"
    assert response.options[1].respondent_count == 0
    assert response.options[2].text == "test3"
    assert response.options[2].respondent_count == 1000
    assert response.multiple == new_data.multiple
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_text_form_field_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateTextFormField(
        required=True,
        question="test",
        question_entities={domain.BoldEntity(offset=0, length=4)},
        creator_id=owner,
        editor_ids={owner},
        re=re.compile(r".+"),
        ex="test",
    )

    document = await actor.create_form_field(data)

    response = await actor.delete_form_field(proto.DeleteFormField(_id=document.id))

    assert response.kind == domain.FormFieldKind.TEXT
    assert isinstance(response, domain.TextFormField)
    assert response.required == data.required
    assert response.question == data.question
    assert response.question_entities == data.question_entities
    assert response.respondent_count == 0
    assert response.creator_id == owner
    assert response.editor_ids == {owner}
    assert response.re == data.re
    assert response.ex == data.ex
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_choice_form_field_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateChoiceFormField(
        required=True,
        question="test",
        question_entities={domain.BoldEntity(offset=0, length=4)},
        creator_id=owner,
        editor_ids={owner},
        options=[
            domain.ChoiceOption(text="test1"),
            domain.ChoiceOption(text="test2"),
            domain.ChoiceOption(text="test3"),
        ],
        respondent_count=0,
        multiple=False,
    )

    document = await actor.create_form_field(data)

    response = await actor.delete_form_field(proto.DeleteFormField(_id=document.id))

    assert response.kind == domain.FormFieldKind.CHOICE
    assert isinstance(response, domain.ChoiceField)
    assert response.required == data.required
    assert response.question == data.question
    assert response.question_entities == data.question_entities
    assert response.respondent_count == 0
    assert response.creator_id == owner
    assert response.editor_ids == {owner}
    assert len(response.options) == len(data.options)
    assert response.options == data.options
    assert response.multiple == data.multiple
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_text_form_field_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.create_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_choice_form_field_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.create_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_text_form_field_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.read_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_choice_form_field_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.read_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_text_form_field_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.update_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_choice_form_field_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.update_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_text_form_field_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.delete_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_choice_form_field_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.delete_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_text_form_field_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateFormFieldException):
        await actor.create_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_choice_form_field_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateFormFieldException):
        await actor.create_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_text_form_field_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.read_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_choice_form_field_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.read_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_text_form_field_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.update_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_choice_form_field_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.update_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_text_form_field_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.delete_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_choice_form_field_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectFormFieldException):
        await actor.delete_form_field(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_text_form_field_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadFormFieldException):
        await actor.read_form_field(proto.ReadFormField(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_choice_form_field_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadFormFieldException):
        await actor.read_form_field(proto.ReadFormField(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_text_form_field_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateFormFieldException):
        await actor.update_form_field(proto.UpdateTextFormField(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_choice_form_field_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateFormFieldException):
        await actor.update_form_field(
            proto.UpdateChoiceFormField(_id=domain.ObjectID())
        )


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_text_form_field_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteFormFieldException):
        await actor.delete_form_field(proto.DeleteFormField(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_choice_form_field_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteFormFieldException):
        await actor.delete_form_field(proto.DeleteFormField(_id=domain.ObjectID()))
