import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database.allocation as proto
from src.service.base import BaseService

# todo: define all business logic


class AllocationService(BaseService):
    def __init__(self, repo: proto.AllocationDatabaseProtocol):
        self._repo = repo

    async def create(self, allocation: proto.CreateAllocation) -> domain.Allocation:
        try:
            return await self._repo.create_allocation(allocation)
        except Exception as e:
            raise service_exception.CreateAllocationException(
                "failed to create allocation"
            ) from e

    async def read(self, allocation: proto.ReadAllocation) -> domain.Allocation:
        try:
            return await self._repo.read_allocation(allocation)
        except Exception as e:
            raise service_exception.ReadAllocationException(
                "failed to read allocation"
            ) from e

    async def update(self, allocation: proto.UpdateAllocation) -> domain.Allocation:
        try:
            return await self._repo.update_allocation(allocation)
        except Exception as e:
            raise service_exception.UpdateAllocationException(
                "failed to update allocation"
            ) from e

    async def delete(self, allocation: proto.DeleteAllocation) -> domain.Allocation:
        try:
            return await self._repo.delete_allocation(allocation)
        except Exception as e:
            raise service_exception.DeleteAllocationException(
                "failed to delete allocation"
            ) from e
