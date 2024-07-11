import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database.participant as proto
from src.service.base import BaseService

# todo: define all business logic


class ParticipantService(BaseService):
    def __init__(self, repo: proto.ParticipantDatabaseProtocol):
        self._repo = repo

    async def create(self, participant: proto.CreateParticipant) -> domain.Participant:
        try:
            return await self._repo.create_participant(participant)
        except Exception as e:
            raise service_exception.CreateParticipantException(
                "service failed to create participant"
            ) from e

    async def read(self, participant: proto.ReadParticipant) -> domain.Participant:
        try:
            return await self._repo.read_participant(participant)
        except Exception as e:
            raise service_exception.ReadParticipantException(
                "service failed to read participant"
            ) from e

    async def update(self, participant: proto.UpdateParticipant) -> domain.Participant:
        try:
            return await self._repo.update_participant(participant)
        except Exception as e:
            raise service_exception.UpdateParticipantException(
                "service failed to update participant"
            ) from e

    async def delete(self, participant: proto.DeleteParticipant) -> domain.Participant:
        try:
            return await self._repo.delete_participant(participant)
        except Exception as e:
            raise service_exception.DeleteParticipantException(
                "service failed to delete participant"
            ) from e
