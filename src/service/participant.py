import src.domain.model as domain
import src.protocol.internal.database.participant as proto
from src.service.base import BaseService


class ParticipantService(BaseService):
    def __init__(self, repo: proto.ParticipantDatabaseProtocol):
        self._repo = repo

    async def create(self, participant: proto.CreateParticipant) -> domain.Participant:
        raise NotImplementedError()

    async def read(self, participant: proto.ReadParticipant) -> domain.Participant:
        raise NotImplementedError()

    async def update(self, participant: proto.UpdateParticipant) -> domain.Participant:
        raise NotImplementedError()

    async def delete(self, participant: proto.DeleteParticipant) -> domain.Participant:
        raise NotImplementedError()
