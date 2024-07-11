import src.domain.model as domain
import src.protocol.internal.database.allocation as proto
from src.service.base import BaseService


class AllocationService(BaseService):
    def __init__(self, repo: proto.AllocationDatabaseProtocol):
        self._repo = repo

    async def create(self, allocation: proto.CreateAllocation) -> domain.Allocation:
        raise NotImplementedError()

    async def read(self, allocation: proto.ReadAllocation) -> domain.Allocation:
        raise NotImplementedError()

    async def update(self, allocation: proto.UpdateAllocation) -> domain.Allocation:
        raise NotImplementedError()

    async def delete(self, allocation: proto.DeleteAllocation) -> domain.Allocation:
        raise NotImplementedError()
