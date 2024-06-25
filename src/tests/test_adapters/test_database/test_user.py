from collections.abc import Awaitable, Callable
from datetime import datetime

import pytest
from pydantic import BaseModel, ConfigDict

import src.domain.exception.database as exception
import src.domain.model as domain
import src.protocol.internal.database.user as proto
from src.adapter.internal.mongodb.service import MongoDBAdapter


async def _get_mongo():
    return await MongoDBAdapter.create("mongodb://localhost:27017")


type ActorFn = Callable[[], Awaitable[proto.UserDatabaseProtocol]]

param_string = "actor_fn"
param_attrs = [_get_mongo]


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_user_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    data = proto.CreateUser(
        tid=1,
        profile=domain.Profile(
            username="test",
            first_name="test",
            last_name="test",
            gender=domain.Gender.MALE,
            language_code=domain.LanguageCode.EN,
            birthdate=datetime.today().date(),
        ),
        views=0,
    )

    response = await actor.create_user(data)

    assert isinstance(response, domain.User)
    assert response.tid == data.tid
    assert response.profile.username == data.profile.username
    assert response.profile.first_name == data.profile.first_name
    assert response.profile.last_name == data.profile.last_name
    assert response.profile.gender == data.profile.gender
    assert response.profile.language_code == data.profile.language_code
    assert response.profile.birthdate == data.profile.birthdate
    assert response.views == data.views
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_user_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectUserException):
        await actor.create_user(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_user_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    data = proto.CreateUser(
        tid=1,
        profile=domain.Profile(
            username="test",
            first_name="test",
            last_name="test",
            gender=domain.Gender.MALE,
            language_code=domain.LanguageCode.EN,
            birthdate=datetime.today().date(),
        ),
        views=0,
    )

    document = await actor.create_user(data)

    response = await actor.read_user(proto.ReadUser(_id=document.id))

    assert isinstance(response, domain.User)
    assert response.tid == data.tid
    assert response.profile.username == data.profile.username
    assert response.profile.first_name == data.profile.first_name
    assert response.profile.last_name == data.profile.last_name
    assert response.profile.gender == data.profile.gender
    assert response.profile.language_code == data.profile.language_code
    assert response.profile.birthdate == data.profile.birthdate
    assert response.views == data.views
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_user_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectUserException):
        await actor.read_user(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_user_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    data = proto.CreateUser(
        tid=1,
        profile=domain.Profile(
            username="test",
            first_name="test",
            last_name="test",
            gender=domain.Gender.MALE,
            language_code=domain.LanguageCode.EN,
            birthdate=datetime.today().date(),
        ),
        views=0,
    )

    document = await actor.create_user(data)
    new_views = 10

    new_data = proto.UpdateUser(
        _id=document.id,
        views=new_views,
        profile=proto.UpdateProfile(
            username="test2",
            first_name="test2",
            last_name="test2",
            gender=domain.Gender.MALE,
            language_code=domain.LanguageCode.EN,
            birthdate=datetime.today().date(),
        ),
    )

    response = await actor.update_user(new_data)

    assert isinstance(response, domain.User)
    assert response.tid == data.tid
    assert new_data.profile is not None
    assert response.profile.username == new_data.profile.username
    assert response.profile.first_name == new_data.profile.first_name
    assert response.profile.last_name == new_data.profile.last_name
    assert response.profile.gender == new_data.profile.gender
    assert response.profile.language_code == new_data.profile.language_code
    assert response.profile.birthdate == new_data.profile.birthdate
    assert response.views == new_views
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_user_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectUserException):
        await actor.update_user(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_user_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    data = proto.CreateUser(
        tid=1,
        profile=domain.Profile(
            username="test",
            first_name="test",
            last_name="test",
            gender=domain.Gender.MALE,
            language_code=domain.LanguageCode.EN,
            birthdate=datetime.today().date(),
        ),
        views=0,
    )

    document = await actor.create_user(data)

    response = await actor.delete_user(proto.DeleteUser(_id=document.id))

    assert isinstance(response, domain.User)
    assert response.tid == data.tid
    assert response.profile.username == data.profile.username
    assert response.profile.first_name == data.profile.first_name
    assert response.profile.last_name == data.profile.last_name
    assert response.profile.gender == data.profile.gender
    assert response.profile.language_code == data.profile.language_code
    assert response.profile.birthdate == data.profile.birthdate
    assert response.views == data.views
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_user_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectUserException):
        await actor.delete_user(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_user_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadUserException):
        await actor.read_user(proto.ReadUser(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_user_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateUserException):
        await actor.update_user(proto.UpdateUser(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_user_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteUserException):
        await actor.delete_user(proto.DeleteUser(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_user_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateUserException):
        await actor.create_user(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_user_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectUserException):
        await actor.read_user(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_user_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectUserException):
        await actor.update_user(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_user_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectUserException):
        await actor.delete_user(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_user_only_views_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    data = proto.CreateUser(
        tid=1,
        profile=domain.Profile(
            username="test",
            first_name="test",
            last_name="test",
            gender=domain.Gender.MALE,
            language_code=domain.LanguageCode.EN,
            birthdate=datetime.today().date(),
        ),
        views=0,
    )

    document = await actor.create_user(data)

    new_views = 10

    new_data = proto.UpdateUser(
        _id=document.id,
        views=new_views,
    )

    response = await actor.update_user(new_data)

    assert response.tid == data.tid
    assert response.profile.username == document.profile.username
    assert response.profile.first_name == document.profile.first_name
    assert response.profile.last_name == document.profile.last_name
    assert response.profile.gender == document.profile.gender
    assert response.profile.language_code == document.profile.language_code
    assert response.profile.birthdate == document.profile.birthdate
    assert response.views == new_views
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None
