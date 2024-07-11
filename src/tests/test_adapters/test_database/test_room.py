from collections.abc import Awaitable, Callable
from datetime import datetime

import pytest
from pydantic import BaseModel, ConfigDict

import src.domain.exception.database as exception
import src.domain.model as domain
import src.protocol.internal.database.room as proto
from src.adapter.internal.memorydb.service import MemoryDBAdapter
from src.adapter.internal.mongodb.service import MongoDBAdapter


async def _get_mongo():
    return await MongoDBAdapter.create("mongodb://localhost:27017")


async def _get_memory():
    return MemoryDBAdapter()


type ActorFn = Callable[[], Awaitable[proto.RoomDatabaseProtocol]]

param_string = "actor_fn"
param_attrs = [_get_mongo, _get_memory]


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_room_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateRoom(
        name="test",
        capacity=5,
        occupied=2,
        creator_id=owner,
        editors_ids={owner},
        gender_restriction=None,
    )

    response = await actor.create_room(data)

    assert isinstance(response, domain.Room)
    assert response.name == data.name
    assert response.capacity == data.capacity
    assert response.occupied == data.occupied
    assert response.creator_id == owner
    assert response.editors_ids == {owner}
    assert response.gender_restriction is None
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_room_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectRoomException):
        await actor.create_room(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_room_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateRoom(
        name="test",
        capacity=5,
        occupied=2,
        creator_id=owner,
        editors_ids={owner},
        gender_restriction=None,
    )

    document = await actor.create_room(data)

    response = await actor.read_room(proto.ReadRoom(_id=document.id))

    assert isinstance(response, domain.Room)
    assert response.name == data.name
    assert response.capacity == data.capacity
    assert response.occupied == data.occupied
    assert response.creator_id == owner
    assert response.editors_ids == {owner}
    assert response.gender_restriction is None
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_room_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectRoomException):
        await actor.read_room(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_room_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateRoom(
        name="test",
        capacity=5,
        occupied=2,
        creator_id=owner,
        editors_ids={owner},
        gender_restriction=None,
    )

    document = await actor.create_room(data)
    new_editors = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}

    new_data = proto.UpdateRoom(
        _id=document.id,
        name="test2",
        capacity=10,
        occupied=3,
        editors_ids=new_editors,
        gender_restriction=domain.Gender.MALE,
    )

    response = await actor.update_room(new_data)

    assert isinstance(response, domain.Room)
    assert response.name == new_data.name
    assert response.capacity == new_data.capacity
    assert response.occupied == new_data.occupied
    assert response.creator_id == owner
    assert response.editors_ids == new_editors
    assert response.gender_restriction == domain.Gender.MALE
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_room_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectRoomException):
        await actor.update_room(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_room_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()

    data = proto.CreateRoom(
        name="test",
        capacity=5,
        occupied=2,
        creator_id=owner,
        editors_ids={owner},
        gender_restriction=None,
    )

    document = await actor.create_room(data)

    response = await actor.delete_room(proto.DeleteRoom(_id=document.id))

    assert isinstance(response, domain.Room)
    assert response.name == data.name
    assert response.capacity == data.capacity
    assert response.occupied == data.occupied
    assert response.creator_id == owner
    assert response.editors_ids == {owner}
    assert response.gender_restriction is None
    assert isinstance(response.id, domain.ObjectID)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_room_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectRoomException):
        await actor.delete_room(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_room_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadRoomException):
        await actor.read_room(proto.ReadRoom(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_room_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateRoomException):
        await actor.update_room(proto.UpdateRoom(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_room_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteRoomException):
        await actor.delete_room(proto.DeleteRoom(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_room_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateRoomException):
        await actor.create_room(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_room_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectRoomException):
        await actor.read_room(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_room_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectRoomException):
        await actor.update_room(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_room_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.ReflectRoomException):
        await actor.delete_room(data)  # type: ignore
