import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database.preference as proto
from src.service.base import BaseService

# todo: define all business logic


class PreferenceService(BaseService):
    def __init__(self, repo: proto.PreferenceDatabaseProtocol):
        self._repo = repo

    async def create(self, preference: proto.CreatePreference) -> domain.Preference:
        try:
            return await self._repo.create_preference(preference)
        except Exception as e:
            raise service_exception.CreatePreferenceException(
                "service failed to create preference"
            ) from e

    async def read(self, preference: proto.ReadPreference) -> domain.Preference:
        try:
            return await self._repo.read_preference(preference)
        except Exception as e:
            raise service_exception.ReadPreferenceException(
                "service failed to read preference"
            ) from e

    async def update(self, preference: proto.UpdatePreference) -> domain.Preference:
        try:
            return await self._repo.update_preference(preference)
        except Exception as e:
            raise service_exception.UpdatePreferenceException(
                "service failed to update preference"
            ) from e

    async def delete(self, preference: proto.DeletePreference) -> domain.Preference:
        try:
            return await self._repo.delete_preference(preference)
        except Exception as e:
            raise service_exception.DeletePreferenceException(
                "service failed to delete preference"
            ) from e

    async def read_many(
        self, preferences: list[proto.ReadPreference]
    ) -> list[domain.Preference]:
        try:
            documents = await self._repo.read_many_preferences(preferences)
            results = []
            for request, response in zip(preferences, documents, strict=True):
                if response is None:
                    raise service_exception.ReadPreferenceException(
                        f"failed to read preference {request.id}"
                    )

                results.append(response)

            return results
        except service_exception.ServiceException as e:
            raise e
        except ValueError as e:  # raised by zip
            raise service_exception.ReadPreferenceException(
                "failed to read preferences"
            ) from e
        except Exception as e:
            raise service_exception.ReadPreferenceException(
                "failed to read preferences"
            ) from e
