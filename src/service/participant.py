import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.service import common
from src.service.base import BaseService


class ParticipantService(BaseService):
    def __init__(
        self,
        allocatin_repo: proto.AllocationDatabaseProtocol,
        participant_repo: proto.ParticipantDatabaseProtocol,
        room_repo: proto.RoomDatabaseProtocol,
        user_repo: proto.UserDatabaseProtocol,
    ):
        self._allocation_repo = allocatin_repo
        self._participant_repo = participant_repo
        self._room_repo = room_repo
        self._user_repo = user_repo

    async def create(self, participant: proto.CreateParticipant) -> domain.Participant:
        try:
            if not await common.check_user_exist(participant, self._user_repo):
                raise service_exception.CreateParticipantException(
                    "user does not exist"
                )

            if not await common.check_allocation_exist(
                participant, self._allocation_repo
            ):
                raise service_exception.CreateParticipantException(
                    "allocation does not exist"
                )

            if isinstance(participant, proto.CreateAllocatedParticipant):
                if not await common.check_room_exist(participant, self._room_repo):
                    raise service_exception.CreateParticipantException(
                        "room does not exist"
                    )

            return await self._participant_repo.create_participant(participant)
        except service_exception.ServiceException as e:
            raise e
        except Exception as e:
            raise service_exception.CreateParticipantException(
                "service failed to create participant"
            ) from e

    async def read(self, participant: proto.ReadParticipant) -> domain.Participant:
        try:
            return await self._participant_repo.read_participant(participant)
        except Exception as e:
            raise service_exception.ReadParticipantException(
                "service failed to read participant"
            ) from e

    async def update(self, participant: proto.UpdateParticipant) -> domain.Participant:
        try:
            try:
                current = await self._participant_repo.read_participant(
                    proto.ReadParticipant(_id=participant.id)
                )
            except Exception as e:
                raise service_exception.UpdateParticipantException(
                    "participant does not exist"
                ) from e

            if participant.room_id is not None:
                if not await common.check_room_exist(participant, self._room_repo):  # type: ignore
                    raise service_exception.UpdateParticipantException(
                        "room does not exist"
                    )

            if not self.__check_participant_state_change(current, participant):
                raise service_exception.UpdateParticipantException(
                    "invalid state transition"
                )

            if participant.user_id is not None:
                raise service_exception.UpdateParticipantException(
                    "can not change user"
                )

            if participant.allocation_id is not None:
                raise service_exception.UpdateParticipantException(
                    "can not change allocation id"
                )

            return await self._participant_repo.update_participant(participant)
        except Exception as e:
            raise service_exception.UpdateParticipantException(
                "service failed to update participant"
            ) from e

    async def delete(self, participant: proto.DeleteParticipant) -> domain.Participant:
        try:
            return await self._participant_repo.delete_participant(participant)
        except Exception as e:
            raise service_exception.DeleteParticipantException(
                "service failed to delete participant"
            ) from e

    async def read_many(
        self, participants: list[proto.ReadParticipant]
    ) -> list[domain.Participant]:
        try:
            documents = await self._participant_repo.read_many_participants(
                participants
            )
            results = []
            for request, response in zip(participants, documents, strict=True):
                if response is None:
                    raise service_exception.ReadParticipantException(
                        f"failed to read participant {request.id}"
                    )

                results.append(response)

            return results
        except service_exception.ServiceException as e:
            raise e
        except ValueError as e:  # raised by zip
            raise service_exception.ReadParticipantException(
                "failed to read participants"
            ) from e
        except Exception as e:
            raise service_exception.ReadParticipantException(
                "failed to read participants"
            ) from e

    def __check_participant_state_change(
        self, current: domain.Participant, participant: proto.UpdateParticipant
    ) -> bool:
        if participant.state is None:
            return True

        allowed_transitions = {
            domain.ParticipantState.CREATING: [
                domain.ParticipantState.CREATED,
            ],
            domain.ParticipantState.CREATED: [
                domain.ParticipantState.ACTIVE,
            ],
            domain.ParticipantState.ACTIVE: [
                domain.ParticipantState.ALLOCATED,
            ],
            domain.ParticipantState.ALLOCATED: [],
        }

        return participant.state in allowed_transitions[current.state]
