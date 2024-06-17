from abc import ABC, abstractmethod

from src.domain.model.allocation import Allocation


class CreateAllocation: ...


class ReadAllocation: ...


class UpdateAllocation: ...


class DeleteAllocation: ...


class AllocationDatabaseProtocol(ABC):
    @abstractmethod
    def create_allocation(self, allocation: CreateAllocation) -> Allocation: ...

    @abstractmethod
    def read_allocation(self, allocation: ReadAllocation) -> Allocation: ...

    @abstractmethod
    def update_allocation(self, allocation: UpdateAllocation) -> Allocation: ...

    @abstractmethod
    def delete_allocation(self, allocation: DeleteAllocation) -> Allocation: ...
