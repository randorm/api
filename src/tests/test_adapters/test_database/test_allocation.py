from datetime import datetime

import pytest

import src.domain.model as domain
import src.protocol.internal.database.allocation as proto
from src.adapter.internal.mongodb.service import MongoDBAdapter


@pytest.mark.parametrize("actor", [None])
class TestAllocation:
    async def test_create_creating_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ):
        actor = await MongoDBAdapter.create("mongodb://127.0.0.1:27017")
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

        response = await actor.create_allocation(data)

        assert isinstance(response.id, domain.ObjectID)
        assert response.name == "test"
        assert response.due == date
        assert response.state == domain.AllocationState.CREATING
        assert len(response.field_ids) == 0
        assert response.creator_id == owner
        assert isinstance(response.created_at, datetime)
        assert isinstance(response.updated_at, datetime)
        assert response.deleted_at is None
        assert len(response.editor_ids) == 1
        assert response.editor_ids == {owner}

    async def test_create_created_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_create_open_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_create_rooming_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_create_roomed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_create_closed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_create_failed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_read_creating_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_read_created_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_read_open_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_read_rooming_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_read_roomed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_read_closed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_read_failed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_update_creating_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_update_created_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_update_open_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_update_rooming_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_update_roomed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_update_closed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_update_failed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_delete_creating_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_delete_created_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_delete_open_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_delete_rooming_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_delete_roomed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_delete_closed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...

    async def test_delete_failed_allocation(
        self,
        actor: proto.AllocationDatabaseProtocol,
    ): ...
