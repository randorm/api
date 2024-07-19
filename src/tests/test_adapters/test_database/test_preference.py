from collections.abc import Awaitable, Callable
from datetime import datetime

import pytest
from pydantic import BaseModel, ConfigDict

import src.domain.exception.database as exception
import src.domain.model as domain
import src.protocol.internal.database.preference as proto
from src.adapter.internal.database.memorydb.service import MemoryDBAdapter
from src.adapter.internal.database.mongodb.service import MongoDBAdapter


async def _get_mongo():
    return await MongoDBAdapter.create("mongodb://localhost:27017")


async def _get_memory():
    return MemoryDBAdapter()


type ActorFn = Callable[[], Awaitable[proto.PreferenceDatabaseProtocol]]

param_string = "actor_fn"
param_attrs = [_get_mongo, _get_memory]


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_preference_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreatePreference(
        kind=domain.PreferenceKind.MATRIMONY,
        status=domain.PreferenceStatus.PENDING,
        user_id=owner,
        target_id=target,
    )

    response = await actor.create_preference(data)

    assert response.kind == data.kind
    assert response.status == data.status
    assert response.user_id == owner
    assert response.target_id == target
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_preference_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreatePreference(
        kind=domain.PreferenceKind.MATRIMONY,
        status=domain.PreferenceStatus.PENDING,
        user_id=owner,
        target_id=target,
    )

    document = await actor.create_preference(data)

    response = await actor.read_preference(proto.ReadPreference(_id=document.id))

    assert response.kind == data.kind
    assert response.status == data.status
    assert response.user_id == owner
    assert response.target_id == target
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_preference_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreatePreference(
        kind=domain.PreferenceKind.MATRIMONY,
        status=domain.PreferenceStatus.PENDING,
        user_id=owner,
        target_id=target,
    )

    document = await actor.create_preference(data)

    new_data = proto.UpdatePreference(
        _id=document.id,
        kind=domain.PreferenceKind.COURTSHIP,
        status=domain.PreferenceStatus.APPROVED,
    )

    response = await actor.update_preference(new_data)

    assert response.kind == new_data.kind
    assert response.status == new_data.status
    assert response.user_id == owner
    assert response.target_id == target
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_preference_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreatePreference(
        kind=domain.PreferenceKind.MATRIMONY,
        status=domain.PreferenceStatus.PENDING,
        user_id=owner,
        target_id=target,
    )

    document = await actor.create_preference(data)

    response = await actor.delete_preference(proto.DeletePreference(_id=document.id))

    assert response.kind == data.kind
    assert response.status == data.status
    assert response.user_id == owner
    assert response.target_id == target
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert isinstance(response.deleted_at, datetime)


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_preference_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadPreferenceException):
        await actor.read_preference(proto.ReadPreference(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_preference_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdatePreferenceException):
        await actor.update_preference(proto.UpdatePreference(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_preference_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeletePreferenceException):
        await actor.delete_preference(proto.DeletePreference(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_preference_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreatePreferenceException):
        await actor.create_preference(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_preference_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectPreferenceException):
        await actor.read_preference(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_preference_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectPreferenceException):
        await actor.update_preference(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_preference_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectPreferenceException):
        await actor.create_preference(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_preference_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectPreferenceException):
        await actor.read_preference(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_preference_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectPreferenceException):
        await actor.update_preference(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_preference_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectPreferenceException):
        await actor.delete_preference(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_preference_change_kind_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreatePreference(
        kind=domain.PreferenceKind.MATRIMONY,
        status=domain.PreferenceStatus.PENDING,
        user_id=owner,
        target_id=target,
    )

    document = await actor.create_preference(data)

    new_data = proto.UpdatePreference(
        _id=document.id,
        kind=domain.PreferenceKind.COURTSHIP,
        status=domain.PreferenceStatus.APPROVED,
    )

    response = await actor.update_preference(new_data)

    assert response.kind == new_data.kind
    assert response.status == new_data.status
    assert response.user_id == owner
    assert response.target_id == target
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_preference_change_status_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreatePreference(
        kind=domain.PreferenceKind.MATRIMONY,
        status=domain.PreferenceStatus.PENDING,
        user_id=owner,
        target_id=target,
    )

    document = await actor.create_preference(data)

    new_data = proto.UpdatePreference(
        _id=document.id,
        kind=domain.PreferenceKind.COURTSHIP,
        status=domain.PreferenceStatus.APPROVED,
    )

    response = await actor.update_preference(new_data)

    assert response.kind == new_data.kind
    assert response.status == new_data.status
    assert response.user_id == owner
    assert response.target_id == target
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None
