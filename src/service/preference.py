import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.service import common
from src.service.base import BaseService
from src.utils.logger.logger import Logger

log = Logger("preference-service")


class PreferenceService(BaseService):
    def __init__(
        self,
        preference_repo: proto.PreferenceDatabaseProtocol,
        user_repo: proto.UserDatabaseProtocol,
    ):
        self._preference_repo = preference_repo
        self._user_repo = user_repo

    async def create(self, preference: proto.CreatePreference) -> domain.Preference:
        try:
            log.debug("creating new preference")

            log.debug("checking preference user existence")
            if not await common.check_user_exist(preference, self._user_repo):
                raise service_exception.CreatePreferenceException("user does not exist")

            log.debug("checking preference target existence")
            if not await common.check_target_exist(preference, self._user_repo):
                raise service_exception.CreatePreferenceException(
                    "target does not exist"
                )

            log.debug("checking preference existence")
            results = await self._preference_repo.find_preferences(
                proto.FindPreference(
                    user_id=preference.user_id, target_id=preference.target_id
                )
            )

            for result in results:
                if result.status == domain.PreferenceStatus.APPROVED:
                    log.error("target user already approved this user")
                    raise service_exception.CreatePreferenceException(
                        "target user already approved this user"
                    )

                if result.status == domain.PreferenceStatus.REJECTED:
                    log.error("target user already rejected this user")
                    raise service_exception.CreatePreferenceException(
                        "target user already rejected this user"
                    )

                if result.status == domain.PreferenceStatus.PENDING:
                    log.error("user already has pending preference")
                    raise service_exception.CreatePreferenceException(
                        "user already has pending preference"
                    )
            log.debug("creating new preference")
            return await self._preference_repo.create_preference(preference)
        except service_exception.ServiceException as e:
            log.error("failed to create preference with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to create preference with error: {}", e)
            raise service_exception.CreatePreferenceException(
                "service failed to create preference"
            ) from e

    async def read(self, preference: proto.ReadPreference) -> domain.Preference:
        try:
            log.debug(f"reading preference {preference.id}")
            return await self._preference_repo.read_preference(preference)
        except Exception as e:
            log.error("failed to read preference with error: {}", e)
            raise service_exception.ReadPreferenceException(
                "service failed to read preference"
            ) from e

    async def update(self, preference: proto.UpdatePreference) -> domain.Preference:
        try:
            log.debug(f"updating preference {preference.id}")
            try:
                log.debug(f"reading preference {preference.id}")
                current = await self._preference_repo.read_preference(
                    proto.ReadPreference(_id=preference.id)
                )
            except Exception as e:
                log.error("failed to read preference with error: {}", e)
                raise service_exception.UpdatePreferenceException(
                    "preference does not exist"
                ) from e

            log.debug("checking preference user non-updateability")
            if current.user_id is not None:
                log.error("can not change user")
                raise service_exception.UpdatePreferenceException("can not change user")

            log.debug("checking preference target non-updateability")
            if current.target_id is not None:
                log.error("can not change target")
                raise service_exception.UpdatePreferenceException(
                    "can not change target"
                )

            log.debug("checking preference state change")
            if not self.__check_preference_state_change(current, preference):
                log.error("invalid state transition")
                raise service_exception.UpdatePreferenceException(
                    "invalid state transition"
                )

            log.debug(f"updating preference {preference.id}")
            return await self._preference_repo.update_preference(preference)
        except service_exception.ServiceException as e:
            log.error("failed to update preference with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to update preference with error: {}", e)
            raise service_exception.UpdatePreferenceException(
                "service failed to update preference"
            ) from e

    async def delete(self, preference: proto.DeletePreference) -> domain.Preference:
        try:
            log.debug(f"deleting preference {preference.id}")
            return await self._preference_repo.delete_preference(preference)
        except Exception as e:
            log.error("failed to delete preference with error: {}", e)
            raise service_exception.DeletePreferenceException(
                "service failed to delete preference"
            ) from e

    async def read_many(
        self, preferences: list[proto.ReadPreference]
    ) -> list[domain.Preference]:
        try:
            log.debug(
                f"reading preferences {[preference.id for preference in preferences]}"
            )
            documents = await self._preference_repo.read_many_preferences(preferences)
            results = []
            for request, response in zip(preferences, documents, strict=True):
                if response is None:
                    log.error(f"failed to read preference {request.id}")
                    raise service_exception.ReadPreferenceException(
                        f"failed to read preference {request.id}"
                    )

                results.append(response)
            log.info(
                f"read preferences {[preference.id for preference in preferences]}"
            )
            return results
        except service_exception.ServiceException as e:
            log.error("failed to read preferences with error: {}", e)
            raise e
        except ValueError as e:  # raised by zip
            log.error("failed to read preferences with error: {}", e)
            raise service_exception.ReadPreferenceException(
                "failed to read preferences"
            ) from e
        except Exception as e:
            log.error("failed to read preferences with error: {}", e)
            raise service_exception.ReadPreferenceException(
                "failed to read preferences"
            ) from e

    def __check_preference_state_change(
        self, current: domain.Preference, preference: proto.UpdatePreference
    ) -> bool:
        log.debug("checking preference status change")
        if preference.status is None:
            return True

        allowed_transitions = {
            domain.PreferenceStatus.PENDING: [
                domain.PreferenceStatus.APPROVED,
                domain.PreferenceStatus.REJECTED,
            ],
            domain.PreferenceStatus.APPROVED: [
                domain.PreferenceStatus.REJECTED,
            ],
            domain.PreferenceStatus.REJECTED: [],
        }

        log.debug(
            f"checking preference status change from {current.status} to {preference.status}"
        )
        log.debug(f"allowed transitions: {allowed_transitions[current.status]}")

        return preference.status in allowed_transitions[current.status]
