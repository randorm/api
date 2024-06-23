from collections.abc import Awaitable, Callable
from datetime import datetime, timedelta

import pytest
from pydantic import BaseModel, ConfigDict

import src.domain.exception.database as exception
import src.domain.model as domain
import src.protocol.internal.database.allocation as proto
from src.adapter.internal.mongodb.service import MongoDBAdapter


async def _get_mongo():
    return await MongoDBAdapter.create("mongodb://localhost:27017")


type ActorFn = Callable[[], Awaitable[proto.AllocationDatabaseProtocol]]

param_string = "actor_fn"
param_attrs = [_get_mongo]


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_creating_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateCreatingAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
    )
    assert data.state == domain.AllocationState.CREATING

    response = await actor.create_allocation(data)

    assert response.state == domain.AllocationState.CREATING
    assert isinstance(response, domain.CreatingAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_created_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateCreatedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    assert data.state == domain.AllocationState.CREATED

    response = await actor.create_allocation(data)

    assert response.state == domain.AllocationState.CREATED
    assert isinstance(response, domain.CreatedAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_open_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateOpenAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    assert data.state == domain.AllocationState.OPEN

    response = await actor.create_allocation(data)

    assert response.state == domain.AllocationState.OPEN
    assert isinstance(response, domain.OpenAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_rooming_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateRoomingAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    assert data.state == domain.AllocationState.ROOMING

    response = await actor.create_allocation(data)

    assert response.state == domain.AllocationState.ROOMING
    assert isinstance(response, domain.RoomingAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_roomed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateRoomedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    assert data.state == domain.AllocationState.ROOMED

    response = await actor.create_allocation(data)

    assert response.state == domain.AllocationState.ROOMED
    assert isinstance(response, domain.RoomedAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_closed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateClosedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    assert data.state == domain.AllocationState.CLOSED

    response = await actor.create_allocation(data)

    assert response.state == domain.AllocationState.CLOSED
    assert isinstance(response, domain.ClosedAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_failed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateFailedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
    )
    assert data.state == domain.AllocationState.FAILED

    response = await actor.create_allocation(data)

    assert response.state == domain.AllocationState.FAILED
    assert isinstance(response, domain.FailedAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_creating_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateCreatingAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
    )
    document = await actor.create_allocation(data)

    response = await actor.read_allocation(proto.ReadAllocation(_id=document.id))

    assert isinstance(response, domain.CreatingAllocation)
    assert data.name == response.name
    assert (data.due is None) == (response.due is None)
    if data.due is not None:
        assert response.due is not None
        assert data.due.date() == response.due.date()
    assert data.field_ids == response.field_ids
    assert data.creator_id == response.creator_id
    assert data.editor_ids == response.editor_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_created_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateCreatedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.read_allocation(proto.ReadAllocation(_id=document.id))

    assert isinstance(response, domain.CreatedAllocation)
    assert data.name == response.name
    assert (data.due is None) == (response.due is None)
    if data.due is not None:
        assert response.due is not None
        assert data.due.date() == response.due.date()
    assert data.field_ids == response.field_ids
    assert data.creator_id == response.creator_id
    assert data.editor_ids == response.editor_ids
    assert data.participant_ids == response.participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_open_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateOpenAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.read_allocation(proto.ReadAllocation(_id=document.id))

    assert isinstance(response, domain.OpenAllocation)
    assert data.name == response.name
    assert (data.due is None) == (response.due is None)
    if data.due is not None:
        assert response.due is not None
        assert data.due.date() == response.due.date()
    assert data.field_ids == response.field_ids
    assert data.creator_id == response.creator_id
    assert data.editor_ids == response.editor_ids
    assert data.participant_ids == response.participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_rooming_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateRoomingAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.read_allocation(proto.ReadAllocation(_id=document.id))

    assert isinstance(response, domain.RoomingAllocation)
    assert data.name == response.name
    assert (data.due is None) == (response.due is None)
    if data.due is not None:
        assert response.due is not None
        assert data.due.date() == response.due.date()
    assert data.field_ids == response.field_ids
    assert data.creator_id == response.creator_id
    assert data.editor_ids == response.editor_ids
    assert data.participant_ids == response.participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_roomed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateRoomedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.read_allocation(proto.ReadAllocation(_id=document.id))

    assert isinstance(response, domain.RoomedAllocation)
    assert data.name == response.name
    assert (data.due is None) == (response.due is None)
    if data.due is not None:
        assert response.due is not None
        assert data.due.date() == response.due.date()
    assert data.field_ids == response.field_ids
    assert data.creator_id == response.creator_id
    assert data.editor_ids == response.editor_ids
    assert data.participant_ids == response.participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_closed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateClosedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.read_allocation(proto.ReadAllocation(_id=document.id))

    assert isinstance(response, domain.ClosedAllocation)
    assert data.name == response.name
    assert (data.due is None) == (response.due is None)
    if data.due is not None:
        assert response.due is not None
        assert data.due.date() == response.due.date()
    assert data.field_ids == response.field_ids
    assert data.creator_id == response.creator_id
    assert data.editor_ids == response.editor_ids
    assert data.participant_ids == response.participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_failed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateFailedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
    )
    document = await actor.create_allocation(data)

    response = await actor.read_allocation(proto.ReadAllocation(_id=document.id))

    assert isinstance(response, domain.FailedAllocation)
    assert data.name == response.name
    assert (data.due is None) == (response.due is None)
    if data.due is not None:
        assert response.due is not None
        assert data.due.date() == response.due.date()
    assert data.field_ids == response.field_ids
    assert data.creator_id == response.creator_id
    assert data.editor_ids == response.editor_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_creating_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateCreatingAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={owner},
    )
    document = await actor.create_allocation(data)

    new_field_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}
    new_date = (date + timedelta(days=5)).replace(microsecond=0)
    new_editor_ids = {owner, domain.ObjectID(), domain.ObjectID()}

    response = await actor.update_allocation(
        proto.UpdateAllocation(
            _id=document.id,
            name="test2",
            due=new_date,
            field_ids=new_field_ids,
            editor_ids=new_editor_ids,
        )
    )

    assert response.state == domain.AllocationState.CREATING
    assert response.id == document.id
    assert isinstance(response, domain.CreatingAllocation)
    assert response.name == "test2"
    assert response.due == new_date
    assert response.field_ids == new_field_ids
    assert response.editor_ids == new_editor_ids

    # todo: test fail with participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_created_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateCreatedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    new_field_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}
    new_date = (date + timedelta(days=5)).replace(microsecond=0)
    new_editor_ids = {owner, domain.ObjectID(), domain.ObjectID()}
    new_participant_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}

    response = await actor.update_allocation(
        proto.UpdateAllocation(
            _id=document.id,
            name="test2",
            due=new_date,
            field_ids=new_field_ids,
            editor_ids=new_editor_ids,
            participant_ids=new_participant_ids,
        )
    )

    assert response.state == domain.AllocationState.CREATED
    assert response.id == document.id
    assert isinstance(response, domain.CreatedAllocation)
    assert response.name == "test2"
    assert response.due == new_date
    assert response.field_ids == new_field_ids
    assert response.editor_ids == new_editor_ids
    assert response.participant_ids == new_participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_open_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateOpenAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    new_field_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}
    new_date = (date + timedelta(days=5)).replace(microsecond=0)
    new_editor_ids = {owner, domain.ObjectID(), domain.ObjectID()}
    new_participant_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}

    response = await actor.update_allocation(
        proto.UpdateAllocation(
            _id=document.id,
            name="test2",
            due=new_date,
            field_ids=new_field_ids,
            editor_ids=new_editor_ids,
            participant_ids=new_participant_ids,
        )
    )

    assert response.state == domain.AllocationState.OPEN
    assert response.id == document.id
    assert isinstance(response, domain.OpenAllocation)
    assert response.name == "test2"
    assert response.due == new_date
    assert response.field_ids == new_field_ids
    assert response.editor_ids == new_editor_ids
    assert response.participant_ids == new_participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_rooming_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateRoomingAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    new_field_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}
    new_date = (date + timedelta(days=5)).replace(microsecond=0)
    new_editor_ids = {owner, domain.ObjectID(), domain.ObjectID()}
    new_participant_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}

    response = await actor.update_allocation(
        proto.UpdateAllocation(
            _id=document.id,
            name="test2",
            due=new_date,
            field_ids=new_field_ids,
            editor_ids=new_editor_ids,
            participant_ids=new_participant_ids,
        )
    )

    assert response.state == domain.AllocationState.ROOMING
    assert response.id == document.id
    assert isinstance(response, domain.RoomingAllocation)
    assert response.name == "test2"
    assert response.due == new_date
    assert response.field_ids == new_field_ids
    assert response.editor_ids == new_editor_ids
    assert response.participant_ids == new_participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_roomed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateRoomedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    new_field_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}
    new_date = (date + timedelta(days=5)).replace(microsecond=0)
    new_editor_ids = {owner, domain.ObjectID(), domain.ObjectID()}
    new_participant_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}

    response = await actor.update_allocation(
        proto.UpdateAllocation(
            _id=document.id,
            name="test2",
            due=new_date,
            field_ids=new_field_ids,
            editor_ids=new_editor_ids,
            participant_ids=new_participant_ids,
        )
    )

    assert response.state == domain.AllocationState.ROOMED
    assert response.id == document.id
    assert isinstance(response, domain.RoomedAllocation)
    assert response.name == "test2"
    assert response.due == new_date
    assert response.field_ids == new_field_ids
    assert response.editor_ids == new_editor_ids
    assert response.participant_ids == new_participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_closed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateClosedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    new_field_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}
    new_date = (date + timedelta(days=5)).replace(microsecond=0)
    new_editor_ids = {owner, domain.ObjectID(), domain.ObjectID()}
    new_participant_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}

    response = await actor.update_allocation(
        proto.UpdateAllocation(
            _id=document.id,
            name="test2",
            due=new_date,
            field_ids=new_field_ids,
            editor_ids=new_editor_ids,
            participant_ids=new_participant_ids,
        )
    )

    assert response.state == domain.AllocationState.CLOSED
    assert response.id == document.id
    assert isinstance(response, domain.ClosedAllocation)
    assert response.name == "test2"
    assert response.due == new_date
    assert response.field_ids == new_field_ids
    assert response.editor_ids == new_editor_ids
    assert response.participant_ids == new_participant_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_failed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now()
    owner = domain.ObjectID()

    data = proto.CreateFailedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
    )
    document = await actor.create_allocation(data)

    new_field_ids = {domain.ObjectID(), domain.ObjectID(), domain.ObjectID()}
    new_date = (date + timedelta(days=5)).replace(microsecond=0)
    new_editor_ids = {owner, domain.ObjectID(), domain.ObjectID()}

    response = await actor.update_allocation(
        proto.UpdateAllocation(
            _id=document.id,
            name="test2",
            due=new_date,
            field_ids=new_field_ids,
            editor_ids=new_editor_ids,
        )
    )

    assert response.state == domain.AllocationState.FAILED
    assert response.id == document.id
    assert isinstance(response, domain.FailedAllocation)
    assert response.name == "test2"
    assert response.due == new_date
    assert response.field_ids == new_field_ids
    assert response.editor_ids == new_editor_ids


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_creating_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now().replace(microsecond=0)
    owner = domain.ObjectID()

    data = proto.CreateCreatingAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
    )
    document = await actor.create_allocation(data)

    response = await actor.delete_allocation(proto.DeleteAllocation(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.AllocationState.CREATING
    assert isinstance(response, domain.CreatingAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_created_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now().replace(microsecond=0)
    owner = domain.ObjectID()

    data = proto.CreateCreatedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.delete_allocation(proto.DeleteAllocation(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.AllocationState.CREATED
    assert isinstance(response, domain.CreatedAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_open_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now().replace(microsecond=0)
    owner = domain.ObjectID()

    data = proto.CreateOpenAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.delete_allocation(proto.DeleteAllocation(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.AllocationState.OPEN
    assert isinstance(response, domain.OpenAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_rooming_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now().replace(microsecond=0)
    owner = domain.ObjectID()

    data = proto.CreateRoomingAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.delete_allocation(proto.DeleteAllocation(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.AllocationState.ROOMING
    assert isinstance(response, domain.RoomingAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_roomed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now().replace(microsecond=0)
    owner = domain.ObjectID()

    data = proto.CreateRoomedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.delete_allocation(proto.DeleteAllocation(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.AllocationState.ROOMED
    assert isinstance(response, domain.RoomedAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_closed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now().replace(microsecond=0)
    owner = domain.ObjectID()

    data = proto.CreateClosedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
        participant_ids=set(),
    )
    document = await actor.create_allocation(data)

    response = await actor.delete_allocation(proto.DeleteAllocation(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.AllocationState.CLOSED
    assert isinstance(response, domain.ClosedAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}
    assert len(response.participant_ids) == 0


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_failed_allocation_ok(actor_fn: ActorFn):
    actor = await actor_fn()
    date = datetime.now().replace(microsecond=0)
    owner = domain.ObjectID()

    data = proto.CreateFailedAllocation(
        name="test",
        due=date,
        field_ids=set(),
        creator_id=owner,
        editor_ids={
            owner,
        },
    )
    document = await actor.create_allocation(data)

    response = await actor.delete_allocation(proto.DeleteAllocation(_id=document.id))

    assert response.deleted_at is not None
    assert response.state == domain.AllocationState.FAILED
    assert isinstance(response, domain.FailedAllocation)
    assert isinstance(response.id, domain.ObjectID)
    assert response.name == "test"
    assert response.due == date
    assert len(response.field_ids) == 0
    assert response.creator_id == owner
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    assert response.deleted_at is not None
    assert len(response.editor_ids) == 1
    assert response.editor_ids == {owner}


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_creating_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_created_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_open_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_rooming_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_roomed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_closed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_failed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_creating_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.read_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_created_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.read_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_open_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.read_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_rooming_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.read_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_roomed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.read_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_closed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.read_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_failed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.read_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_creating_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.update_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_created_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.update_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_open_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.update_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_rooming_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.update_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_roomed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.update_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_closed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.update_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_failed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.update_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_creating_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.delete_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_created_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.delete_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_open_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.delete_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_rooming_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.delete_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_roomed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.delete_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_closed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.delete_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_failed_allocation_reflect_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    class MutableObject(BaseModel):
        model_config = ConfigDict(extra="allow")

    data = MutableObject()
    with pytest.raises(exception.ReflectAlloctionException):
        await actor.delete_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_creating_allocation_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateAllocationException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_created_allocation_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateAllocationException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_open_allocation_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateAllocationException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_rooming_allocation_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateAllocationException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_roomed_allocation_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateAllocationException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_closed_allocation_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateAllocationException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_create_failed_allocation_immutable_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = object
    with pytest.raises(exception.CreateAllocationException):
        await actor.create_allocation(data)  # type: ignore


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_creating_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadAllocationException):
        await actor.read_allocation(proto.ReadAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_created_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadAllocationException):
        await actor.read_allocation(proto.ReadAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_open_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadAllocationException):
        await actor.read_allocation(proto.ReadAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_rooming_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadAllocationException):
        await actor.read_allocation(proto.ReadAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_roomed_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadAllocationException):
        await actor.read_allocation(proto.ReadAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_closed_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadAllocationException):
        await actor.read_allocation(proto.ReadAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_read_failed_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.ReadAllocationException):
        await actor.read_allocation(proto.ReadAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_creating_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateAllocationException):
        await actor.update_allocation(proto.UpdateAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_created_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateAllocationException):
        await actor.update_allocation(proto.UpdateAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_open_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateAllocationException):
        await actor.update_allocation(proto.UpdateAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_rooming_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateAllocationException):
        await actor.update_allocation(proto.UpdateAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_roomed_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateAllocationException):
        await actor.update_allocation(proto.UpdateAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_closed_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateAllocationException):
        await actor.update_allocation(proto.UpdateAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_failed_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.UpdateAllocationException):
        await actor.update_allocation(proto.UpdateAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_creating_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteAllocationException):
        await actor.delete_allocation(proto.DeleteAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_created_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteAllocationException):
        await actor.delete_allocation(proto.DeleteAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_open_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteAllocationException):
        await actor.delete_allocation(proto.DeleteAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_rooming_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteAllocationException):
        await actor.delete_allocation(proto.DeleteAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_roomed_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteAllocationException):
        await actor.delete_allocation(proto.DeleteAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_closed_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteAllocationException):
        await actor.delete_allocation(proto.DeleteAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_delete_failed_allocation_not_exist_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    with pytest.raises(exception.DeleteAllocationException):
        await actor.delete_allocation(proto.DeleteAllocation(_id=domain.ObjectID()))


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_allocation_change_state_ok(actor_fn: ActorFn):
    actor = await actor_fn()

    data = proto.CreateCreatingAllocation(
        name="test",
        due=datetime.now(),
        field_ids=set(),
        creator_id=domain.ObjectID(),
        editor_ids={
            domain.ObjectID(),
        },
    )
    document = await actor.create_allocation(data)

    new_data = proto.UpdateAllocation(
        _id=document.id,
        state=domain.AllocationState.CREATED,
        participant_ids={domain.ObjectID() for _ in range(10)},
    )
    document = await actor.update_allocation(new_data)

    assert document.id == new_data.id
    assert document.state == domain.AllocationState.CREATED
    assert isinstance(document, domain.CreatedAllocation)
    assert len(document.participant_ids) == 10


@pytest.mark.parametrize(param_string, param_attrs)
async def test_update_creating_allocation_change_participant_fail(actor_fn: ActorFn):
    actor = await actor_fn()

    data = proto.CreateCreatingAllocation(
        name="test",
        due=datetime.now(),
        field_ids=set(),
        creator_id=domain.ObjectID(),
        editor_ids={
            domain.ObjectID(),
        },
    )
    document = await actor.create_allocation(data)

    new_data = proto.UpdateAllocation(
        _id=document.id,
        participant_ids={domain.ObjectID() for _ in range(10)},
    )
    with pytest.raises(exception.UpdateAllocationException):
        document = await actor.update_allocation(new_data)
