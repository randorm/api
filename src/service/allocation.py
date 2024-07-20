import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.service import common
from src.service.base import BaseService


class AllocationService(BaseService):
    def __init__(
        self,
        allocation_repo: proto.AllocationDatabaseProtocol,
        form_field_repo: proto.FormFieldDatabaseProtocol,
        participant_repo: proto.ParticipantDatabaseProtocol,
        user_repo: proto.UserDatabaseProtocol,
    ):
        self._allocation_repo = allocation_repo
        self._form_field_repo = form_field_repo
        self._participant_repo = participant_repo
        self._user_repo = user_repo

    async def create(self, allocation: proto.CreateAllocation) -> domain.Allocation:
        try:
            if not await common.check_creator_exist(allocation, self._user_repo):
                raise service_exception.CreateAllocationException(
                    "creator does not exist"
                )

            if not await common.check_editors_exist(allocation, self._user_repo):
                raise service_exception.CreateAllocationException(
                    "one or more editors do not exist"
                )

            if not await common.check_form_fields_exist(
                allocation, self._form_field_repo
            ):
                raise service_exception.CreateAllocationException(
                    "one or more form fields does not exist"
                )

            # if allocation.due is not None:
            #     if allocation.due < datetime.now():
            #         raise service_exception.CreateAllocationException(
            #             "due date is in the past"
            #         )

            if isinstance(
                allocation,
                proto.CreateCreatedAllocation
                | proto.CreateOpenAllocation
                | proto.CreateRoomingAllocation
                | proto.CreateRoomedAllocation
                | proto.CreateClosedAllocation,
            ):
                if not await common.check_participants_exist(
                    allocation, self._participant_repo
                ):
                    raise service_exception.CreateAllocationException(
                        "one or more participants does not exist"
                    )

            return await self._allocation_repo.create_allocation(allocation)
        except service_exception.ServiceException as e:
            raise e
        except Exception as e:
            raise service_exception.CreateAllocationException(
                "failed to create allocation"
            ) from e

    async def read(self, allocation: proto.ReadAllocation) -> domain.Allocation:
        try:
            return await self._allocation_repo.read_allocation(allocation)
        except Exception as e:
            raise service_exception.ReadAllocationException(
                "failed to read allocation"
            ) from e

    async def update(self, allocation: proto.UpdateAllocation) -> domain.Allocation:
        try:
            try:
                current = await self._allocation_repo.read_allocation(
                    proto.ReadAllocation(_id=allocation.id)
                )
            except Exception as e:
                raise service_exception.UpdateAllocationException(
                    "allocation does not exist"
                ) from e

            if not self.__check_allocation_state_change(current, allocation):
                raise service_exception.UpdateAllocationException(
                    "invalid state transition"
                )

            # if allocation.editors_ids is not None:
            #     if not await common.check_editors_exist(allocation, self._user_repo):  # type: ignore
            #         raise service_exception.UpdateAllocationException(
            #             "one or more editors do not exist"
            #         )

            if allocation.form_fields_ids is not None:
                if not await common.check_form_fields_exist(
                    allocation,
                    self._form_field_repo,  # type: ignore
                ):
                    raise service_exception.UpdateAllocationException(
                        "one or more form fields does not exist"
                    )

            if allocation.creator_id is not None:
                raise service_exception.UpdateAllocationException(
                    "creator cannot be updated"
                )

            return await self._allocation_repo.update_allocation(allocation)
        except service_exception.ServiceException as e:
            raise e
        except Exception as e:
            raise service_exception.UpdateAllocationException(
                "failed to update allocation"
            ) from e

    async def delete(self, allocation: proto.DeleteAllocation) -> domain.Allocation:
        try:
            return await self._allocation_repo.delete_allocation(allocation)
        except Exception as e:
            raise service_exception.DeleteAllocationException(
                "failed to delete allocation"
            ) from e

    async def read_many(
        self, allocations: list[proto.ReadAllocation]
    ) -> list[domain.Allocation]:
        try:
            documents = await self._allocation_repo.read_many_allocations(allocations)
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

    def __check_allocation_state_change(
        self, current: domain.Allocation, allocation: proto.UpdateAllocation
    ) -> bool:
        if allocation.state is None:
            return True

        allowed_transitions = {
            domain.AllocationState.CREATING: [
                domain.AllocationState.CREATED,
                domain.AllocationState.FAILED,
            ],
            domain.AllocationState.CREATED: [
                domain.AllocationState.OPEN,
                domain.AllocationState.FAILED,
            ],
            domain.AllocationState.OPEN: [
                domain.AllocationState.ROOMING,
                domain.AllocationState.FAILED,
            ],
            domain.AllocationState.ROOMING: [
                domain.AllocationState.ROOMED,
                domain.AllocationState.FAILED,
            ],
            domain.AllocationState.ROOMED: [
                domain.AllocationState.CLOSED,
                domain.AllocationState.FAILED,
            ],
            domain.AllocationState.CLOSED: [
                domain.AllocationState.FAILED,
            ],
            domain.AllocationState.FAILED: [],
        }

        return allocation.state in allowed_transitions[current.state]
