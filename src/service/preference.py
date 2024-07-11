import src.domain.model as domain
import src.protocol.internal.database.preference as proto
from src.service.base import BaseService


class PreferenceService(BaseService):
    def __init__(self, repo: proto.PreferenceDatabaseProtocol):
        self._repo = repo

    async def create(self, preference: proto.CreatePreference) -> domain.Preference:
        raise NotImplementedError()

    async def read(self, preference: proto.ReadPreference) -> domain.Preference:
        raise NotImplementedError()

    async def update(self, preference: proto.UpdatePreference) -> domain.Preference:
        raise NotImplementedError()

    async def delete(self, preference: proto.DeletePreference) -> domain.Preference:
        raise NotImplementedError()
