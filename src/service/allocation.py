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

    async def read_many(
        self, allocations: list[proto.ReadAllocation]
    ) -> list[domain.Allocation]:
        try:
            documents = await self._repo.read_many_allocations(allocations)
            results = []
            for request, response in zip(allocations, documents, strict=True):
                if response is None:
                    raise service_exception.ReadAllocationException(
                        f"failed to read allocation {request.id}"
                    )

                results.append(response)

            return results
        except service_exception.ServiceException as e:
            raise e
        except ValueError as e:  # raised by zip
            raise service_exception.ReadAllocationException(
                "failed to read allocations"
            ) from e
        except Exception as e:
            raise service_exception.ReadAllocationException(
                "failed to read allocations"
            ) from e
