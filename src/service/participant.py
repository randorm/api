import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.service import common
from src.service.base import BaseService
from src.utils.logger.logger import Logger

log = Logger("participant-service")


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
            log.debug("creating new participant")

            log.debug("checking participant user existence")
            if not await common.check_user_exist(participant, self._user_repo):
                log.error("user does not exist")
                raise service_exception.CreateParticipantException(
                    "user does not exist"
                )

            log.debug("checking participant allocation existence")
            if not await common.check_allocation_exist(
                participant, self._allocation_repo
            ):
                log.error("allocation does not exist")
                raise service_exception.CreateParticipantException(
                    "allocation does not exist"
                )

            if isinstance(participant, proto.CreateAllocatedParticipant):
                log.debug("checking participant room existence")
                if not await common.check_room_exist(participant, self._room_repo):
                    log.error("room does not exist")
                    raise service_exception.CreateParticipantException(
                        "room does not exist"
                    )

            log.debug("creating new participant")
            return await self._participant_repo.create_participant(participant)
        except service_exception.ServiceException as e:
            log.error("failed to create participant with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to create participant with error: {}", e)
            raise service_exception.CreateParticipantException(
                "service failed to create participant"
            ) from e

    async def read(self, participant: proto.ReadParticipant) -> domain.Participant:
        try:
            log.debug(f"reading participant {participant.id}")
            return await self._participant_repo.read_participant(participant)
        except Exception as e:
            log.error("failed to read participant with error: {}", e)
            raise service_exception.ReadParticipantException(
                "service failed to read participant"
            ) from e

    async def update(self, participant: proto.UpdateParticipant) -> domain.Participant:
        try:
            log.debug(f"updating participant {participant.id}")
            try:
                log.debug(f"reading participant {participant.id}")
                current = await self._participant_repo.read_participant(
                    proto.ReadParticipant(_id=participant.id)
                )
            except Exception as e:
                log.error("failed to read participant with error: {}", e)
                raise service_exception.UpdateParticipantException(
                    "participant does not exist"
                ) from e

            log.debug("checking participant room existence")
            if participant.room_id is not None:
                log.debug("checking participant room existence")
                if not await common.check_room_exist(participant, self._room_repo):  # type: ignore
                    log.error("room does not exist")
                    raise service_exception.UpdateParticipantException(
                        "room does not exist"
                    )

            log.debug("checking participant state change")
            if not self.__check_participant_state_change(current, participant):
                log.error("invalid state transition")
                raise service_exception.UpdateParticipantException(
                    "invalid state transition"
                )
            log.debug("checking participant user non-updateability")
            if participant.user_id is not None:
                log.error("can not change user")
                raise service_exception.UpdateParticipantException(
                    "can not change user"
                )

            log.debug("checking participant allocation non-updateability")
            if participant.allocation_id is not None:
                log.error("can not change allocation id")
                raise service_exception.UpdateParticipantException(
                    "can not change allocation id"
                )

            log.debug(f"updating participant {participant.id}")
            return await self._participant_repo.update_participant(participant)
        except Exception as e:
            log.error("failed to update participant with error: {}", e)
            raise service_exception.UpdateParticipantException(
                "service failed to update participant"
            ) from e

    async def delete(self, participant: proto.DeleteParticipant) -> domain.Participant:
        try:
            log.debug(f"deleting participant {participant.id}")
            return await self._participant_repo.delete_participant(participant)
        except Exception as e:
            log.error("failed to delete participant with error: {}", e)
            raise service_exception.DeleteParticipantException(
                "service failed to delete participant"
            ) from e

    async def read_many(
        self, participants: list[proto.ReadParticipant]
    ) -> list[domain.Participant]:
        try:
            log.debug(
                f"reading participants {[participant.id for participant in participants]}"
            )
            documents = await self._participant_repo.read_many_participants(
                participants
            )
            results = []
            for request, response in zip(participants, documents, strict=True):
                if response is None:
                    log.error(f"failed to read participant {request.id}")
                    raise service_exception.ReadParticipantException(
                        f"failed to read participant {request.id}"
                    )

                results.append(response)

            log.info(
                f"read participants {[participant.id for participant in participants]}"
            )
            return results
        except service_exception.ServiceException as e:
            log.error("failed to read participants with error: {}", e)
            raise e
        except ValueError as e:  # raised by zip
            log.error("failed to read participants with error: {}", e)
            raise service_exception.ReadParticipantException(
                "failed to read participants"
            ) from e
        except Exception as e:
            log.error("failed to read participants with error: {}", e)
            raise service_exception.ReadParticipantException(
                "failed to read participants"
            ) from e

    def __check_participant_state_change(
        self, current: domain.Participant, participant: proto.UpdateParticipant
    ) -> bool:
        log.debug("checking participant state change")
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

        log.debug(
            f"checking participant state change from {current.state} to {participant.state}"
        )
        log.debug(f"allowed transitions: {allowed_transitions[current.state]}")

        return participant.state in allowed_transitions[current.state]
