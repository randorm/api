from collections.abc import Awaitable, Callable

import pytest
from pydantic import BaseModel, ConfigDict

import src.domain.exception.database as exception
import src.domain.model as domain
import src.protocol.internal.database.participant as proto
from src.adapter.internal.memorydb.service import MemoryDBAdapter
from src.adapter.internal.mongodb.service import MongoDBAdapter


async def _get_mongo():
    return await MongoDBAdapter.create("mongodb://localhost:27017")


async def _get_memory():
    return MemoryDBAdapter()


type ActorFn = Callable[[], Awaitable[proto.ParticipantDatabaseProtocol]]

param_string = "actor_fn"
param_attrs = [_get_mongo, _get_memory]


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_creating_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateCreatingParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    response = await actor.create_participant(data)

    assert response.state == domain.ParticipantState.CREATING
    assert isinstance(response, domain.CreatingParticipant)
    assert isinstance(response.id, domain.ObjectID)
    assert response.allocation_id == allocation_id
    assert response.user_id == user_id
    assert len(response.viewed_ids) == 2
    assert len(response.subscription_ids) == 1
    assert len(response.subscribers_ids) == 1


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_created_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateCreatedParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    response = await actor.create_participant(data)

    assert response.state == domain.ParticipantState.CREATED
    assert isinstance(response, domain.CreatedParticipant)
    assert isinstance(response.id, domain.ObjectID)
    assert response.allocation_id == allocation_id
    assert response.user_id == user_id
    assert len(response.viewed_ids) == 2
    assert len(response.subscription_ids) == 1
    assert len(response.subscribers_ids) == 1


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_active_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateActiveParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    response = await actor.create_participant(data)

    assert response.state == domain.ParticipantState.ACTIVE
    assert isinstance(response, domain.ActiveParticipant)
    assert isinstance(response.id, domain.ObjectID)
    assert response.allocation_id == allocation_id
    assert response.user_id == user_id
    assert len(response.viewed_ids) == 2
    assert len(response.subscription_ids) == 1
    assert len(response.subscribers_ids) == 1


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_allocated_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()
    room_id = domain.ObjectID()

    data = proto.CreateAllocatedParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
        room_id=room_id,
    )

    response = await actor.create_participant(data)

    assert response.state == domain.ParticipantState.ALLOCATED
    assert isinstance(response, domain.AllocatedParticipant)
    assert isinstance(response.id, domain.ObjectID)
    assert response.allocation_id == allocation_id
    assert response.user_id == user_id
    assert response.room_id == room_id
    assert response.viewed_ids == {person1, person2}
    assert response.subscription_ids == {person1}
    assert response.subscribers_ids == {person3}


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_creating_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateCreatingParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    document = await actor.create_participant(data)

    response = await actor.read_participant(proto.ReadParticipant(_id=document.id))

    assert isinstance(response, domain.CreatingParticipant)
    assert data.allocation_id == response.allocation_id
    assert data.user_id == response.user_id
    assert data.viewed_ids == response.viewed_ids
    assert data.subscription_ids == response.subscription_ids
    assert data.subscribers_ids == response.subscribers_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_created_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateCreatedParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    document = await actor.create_participant(data)

    response = await actor.read_participant(proto.ReadParticipant(_id=document.id))

    assert isinstance(response, domain.CreatedParticipant)
    assert data.allocation_id == response.allocation_id
    assert data.user_id == response.user_id
    assert data.viewed_ids == response.viewed_ids
    assert data.subscription_ids == response.subscription_ids
    assert data.subscribers_ids == response.subscribers_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_active_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateActiveParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    document = await actor.create_participant(data)

    response = await actor.read_participant(proto.ReadParticipant(_id=document.id))

    assert isinstance(response, domain.ActiveParticipant)
    assert data.allocation_id == response.allocation_id
    assert data.user_id == response.user_id
    assert data.viewed_ids == response.viewed_ids
    assert data.subscription_ids == response.subscription_ids
    assert data.subscribers_ids == response.subscribers_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_allocated_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()
    room_id = domain.ObjectID()

    data = proto.CreateAllocatedParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
        room_id=room_id,
    )

    document = await actor.create_participant(data)

    response = await actor.read_participant(proto.ReadParticipant(_id=document.id))

    assert isinstance(response, domain.AllocatedParticipant)
    assert data.allocation_id == response.allocation_id
    assert data.user_id == response.user_id
    assert data.room_id == response.room_id
    assert data.viewed_ids == response.viewed_ids
    assert data.subscription_ids == response.subscription_ids
    assert data.subscribers_ids == response.subscribers_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_creating_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateCreatingParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    document = await actor.create_participant(data)

    new_data = proto.UpdateParticipant(
        _id=document.id,
        viewed_ids={person2, person3},
        subscription_ids={person2},
        subscribers_ids={person3},
    )

    response = await actor.update_participant(new_data)

    assert response.id == new_data.id
    assert response.allocation_id == data.allocation_id
    assert response.user_id == data.user_id
    assert response.viewed_ids == new_data.viewed_ids
    assert response.subscription_ids == new_data.subscription_ids
    assert response.subscribers_ids == new_data.subscribers_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_active_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateActiveParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    document = await actor.create_participant(data)

    new_data = proto.UpdateParticipant(
        _id=document.id,
        viewed_ids={person2, person3},
        subscription_ids={person2},
        subscribers_ids={person3},
    )

    response = await actor.update_participant(new_data)

    assert response.id == new_data.id
    assert response.allocation_id == data.allocation_id
    assert response.user_id == data.user_id
    assert response.viewed_ids == new_data.viewed_ids
    assert response.subscription_ids == new_data.subscription_ids
    assert response.subscribers_ids == new_data.subscribers_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_allocated_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()
    room_id = domain.ObjectID()

    data = proto.CreateAllocatedParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
        room_id=room_id,
    )

    document = await actor.create_participant(data)

    new_data = proto.UpdateParticipant(
        _id=document.id,
        viewed_ids={person2, person3},
        subscription_ids={person2},
        subscribers_ids={person3},
    )

    response = await actor.update_participant(new_data)

    assert isinstance(response, domain.AllocatedParticipant)
    assert response.id == new_data.id
    assert response.allocation_id == data.allocation_id
    assert response.user_id == data.user_id
    assert response.room_id == data.room_id
    assert response.viewed_ids == new_data.viewed_ids
    assert response.subscription_ids == new_data.subscription_ids
    assert response.subscribers_ids == new_data.subscribers_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_creating_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateCreatingParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    document = await actor.create_participant(data)

    response = await actor.delete_participant(proto.DeleteParticipant(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.ParticipantState.CREATING
    assert isinstance(response, domain.CreatingParticipant)
    assert isinstance(response.id, domain.ObjectID)
    assert response.allocation_id == allocation_id
    assert response.user_id == user_id
    assert len(response.viewed_ids) == 2
    assert len(response.subscription_ids) == 1
    assert len(response.subscribers_ids) == 1


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_created_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateCreatedParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    document = await actor.create_participant(data)

    response = await actor.delete_participant(proto.DeleteParticipant(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.ParticipantState.CREATED
    assert isinstance(response, domain.CreatedParticipant)
    assert isinstance(response.id, domain.ObjectID)
    assert response.allocation_id == allocation_id
    assert response.user_id == user_id
    assert len(response.viewed_ids) == 2
    assert len(response.subscription_ids) == 1
    assert len(response.subscribers_ids) == 1


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_active_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateActiveParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    document = await actor.create_participant(data)

    response = await actor.delete_participant(proto.DeleteParticipant(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.ParticipantState.ACTIVE
    assert isinstance(response, domain.ActiveParticipant)
    assert isinstance(response.id, domain.ObjectID)
    assert response.allocation_id == allocation_id
    assert response.user_id == user_id
    assert len(response.viewed_ids) == 2
    assert len(response.subscription_ids) == 1
    assert len(response.subscribers_ids) == 1


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_allocated_participant_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()
    room_id = domain.ObjectID()

    data = proto.CreateAllocatedParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
        room_id=room_id,
    )

    document = await actor.create_participant(data)

    response = await actor.delete_participant(proto.DeleteParticipant(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.ParticipantState.ALLOCATED
    assert isinstance(response, domain.AllocatedParticipant)
    assert isinstance(response.id, domain.ObjectID)
    assert response.allocation_id == allocation_id
    assert response.user_id == user_id
    assert response.room_id == room_id
    assert len(response.viewed_ids) == 2
    assert len(response.subscription_ids) == 1


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_participant_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectParticipantException):
        await actor.create_participant(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_participant_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectParticipantException):
        await actor.read_participant(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_participant_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectParticipantException):
        await actor.update_participant(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_participant_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectParticipantException):
        await actor.delete_participant(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_participant_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateParticipantException):
        await actor.create_participant(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_participant_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadParticipantException):
        await actor.read_participant(proto.ReadParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_participant_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateParticipantException):
        await actor.update_participant(proto.UpdateParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_participant_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteParticipantException):
        await actor.delete_participant(proto.DeleteParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_creating_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadParticipantException):
        await actor.read_participant(proto.ReadParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_creating_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateParticipantException):
        await actor.update_participant(proto.UpdateParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_creating_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteParticipantException):
        await actor.delete_participant(proto.DeleteParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_created_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadParticipantException):
        await actor.read_participant(proto.ReadParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_created_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateParticipantException):
        await actor.update_participant(proto.UpdateParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_created_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteParticipantException):
        await actor.delete_participant(proto.DeleteParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_active_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadParticipantException):
        await actor.read_participant(proto.ReadParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_active_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateParticipantException):
        await actor.update_participant(proto.UpdateParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_active_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteParticipantException):
        await actor.delete_participant(proto.DeleteParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_allocated_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadParticipantException):
        await actor.read_participant(proto.ReadParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_allocated_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateParticipantException):
        await actor.update_participant(proto.UpdateParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_allocated_participant_does_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteParticipantException):
        await actor.delete_participant(proto.DeleteParticipant(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_upadte_participant_change_state_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    allocation_id = domain.ObjectID()
    user_id = domain.ObjectID()
    person1 = domain.ObjectID()
    person2 = domain.ObjectID()
    person3 = domain.ObjectID()

    data = proto.CreateCreatingParticipant(
        allocation_id=allocation_id,
        user_id=user_id,
        viewed_ids={person1, person2},
        subscription_ids={person1},
        subscribers_ids={person3},
    )

    document = await actor.create_participant(data)

    new_data = proto.UpdateParticipant(
        _id=document.id,
        viewed_ids={person2, person3},
        subscription_ids={person2},
        subscribers_ids={person3},
        state=domain.ParticipantState.CREATED,
    )

    response = await actor.update_participant(new_data)

    assert isinstance(response, domain.CreatedParticipant)
    assert response.id == new_data.id
    assert response.allocation_id == data.allocation_id
    assert response.user_id == data.user_id
    assert response.viewed_ids == new_data.viewed_ids
    assert response.subscription_ids == new_data.subscription_ids
    assert response.subscribers_ids == new_data.subscribers_ids
    assert response.state == domain.ParticipantState.CREATED


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_participant_change_room_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreateAllocatedParticipant(
        user_id=owner,
        allocation_id=target,
        room_id=domain.ObjectID(),
        state=domain.ParticipantState.ALLOCATED,
    )

    document = await actor.create_participant(data)

    new_data = proto.UpdateParticipant(
        _id=document.id,
        room_id=domain.ObjectID(),
    )

    response = await actor.update_participant(new_data)

    assert isinstance(response, domain.AllocatedParticipant)
    assert response.id == new_data.id
    assert response.allocation_id == data.allocation_id
    assert response.user_id == data.user_id
    assert response.room_id == new_data.room_id
    assert response.state == domain.ParticipantState.ALLOCATED


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_creating_participant_room_fail(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreateCreatingParticipant(
        user_id=owner,
        allocation_id=target,
        state=domain.ParticipantState.CREATING,
    )

    document = await actor.create_participant(data)

    new_data = proto.UpdateParticipant(
        _id=document.id,
        room_id=domain.ObjectID(),
    )

    with pytest.raises(exception.UpdateParticipantException):
        await actor.update_participant(new_data)


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_created_participant_room_fail(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreateCreatedParticipant(
        user_id=owner,
        allocation_id=target,
        state=domain.ParticipantState.CREATED,
    )

    document = await actor.create_participant(data)

    new_data = proto.UpdateParticipant(
        _id=document.id,
        room_id=domain.ObjectID(),
    )

    with pytest.raises(exception.UpdateParticipantException):
        await actor.update_participant(new_data)


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_active_participant_room_fail(actor_fn: ActorFn):
    actor = await actor_fn()
    owner = domain.ObjectID()
    target = domain.ObjectID()

    data = proto.CreateActiveParticipant(
        user_id=owner,
        allocation_id=target,
        state=domain.ParticipantState.ACTIVE,
    )

    document = await actor.create_participant(data)

    new_data = proto.UpdateParticipant(
        _id=document.id,
        room_id=domain.ObjectID(),
    )

    with pytest.raises(exception.UpdateParticipantException):
        await actor.update_participant(new_data)
