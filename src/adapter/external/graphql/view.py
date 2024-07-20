import strawberry as sb
from strawberry.aiohttp.views import GraphQLView
from strawberry.dataloader import DataLoader, DefaultCache

from src.adapter.external.graphql.query import Query
from src.adapter.external.graphql.tool.context import Context, DataContext
from src.adapter.external.graphql.type.allocation import (
    AllocationType,
    domain_to_allocation,
)
from src.adapter.external.graphql.type.form_field import (
    FormFieldType,
    domain_to_form_field,
)
from src.adapter.external.graphql.type.participant import (
    ParticipantType,
    domain_to_participant,
)
from src.adapter.external.graphql.type.preference import PreferenceType
from src.adapter.external.graphql.type.room import RoomType
from src.adapter.external.graphql.type.user import UserType
from src.domain.model.scalar.object_id import ObjectID
from src.protocol.internal.database.allocation import ReadAllocation
from src.protocol.internal.database.form_field import ReadFormField
from src.protocol.internal.database.participant import ReadParticipant
from src.protocol.internal.database.preference import ReadPreference
from src.protocol.internal.database.room import ReadRoom
from src.protocol.internal.database.user import ReadUser
from src.service.allocation import AllocationService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService

GRAPHQL_SCHEMA = sb.Schema(query=Query)


class CustomDefaultCache[K, T](DefaultCache[K, T]):
    def delete(self, key: K) -> None:
        if key in self.cache_map:
            del self.cache_map[key]


class RandormGraphQLView(GraphQLView):
    def __init__(
        self,
        schema: sb.Schema,
        user_service: UserService,
        allocation_service: AllocationService,
        form_field_service: FormFieldService,
        participant_service: ParticipantService,
        preference_service: PreferenceService,
        room_service: RoomService,
    ):
        self._user_service = user_service
        self._allocation_service = allocation_service
        self._form_field_service = form_field_service
        self._participant_service = participant_service
        self._preference_service = preference_service
        self._room_service = room_service
        super().__init__(schema)

    async def get_context(self, request, response):
        return Context(
            user=DataContext(
                loader=DataLoader(
                    load_fn=self.__load_users,
                    cache_key_fn=str,
                    cache_map=CustomDefaultCache(),
                ),
                service=self._user_service,
            ),
            allocation=DataContext(
                loader=DataLoader(
                    load_fn=self.__load_allocations,
                    cache_key_fn=str,
                    cache_map=CustomDefaultCache(),
                ),
                service=self._allocation_service,
            ),
            form_field=DataContext(
                loader=DataLoader(
                    load_fn=self.__load_form_fields,
                    cache_key_fn=str,
                    cache_map=CustomDefaultCache(),
                ),
                service=self._form_field_service,
            ),
            participant=DataContext(
                loader=DataLoader(
                    load_fn=self.__load_participants,
                    cache_key_fn=str,
                    cache_map=CustomDefaultCache(),
                ),
                service=self._participant_service,
            ),
            preference=DataContext(
                loader=DataLoader(
                    load_fn=self.__load_preferences,
                    cache_key_fn=str,
                    cache_map=CustomDefaultCache(),
                ),
                service=self._preference_service,
            ),
            room=DataContext(
                loader=DataLoader(
                    load_fn=self.__load_rooms,
                    cache_key_fn=str,
                    cache_map=CustomDefaultCache(),
                ),
                service=self._room_service,
            ),
        )

    async def __load_users(self, ids: list[ObjectID]) -> list[UserType]:
        request = [ReadUser(_id=id) for id in ids]
        response = await self._user_service.read_many(request)

        return [UserType.from_pydantic(obj) for obj in response]

    async def __load_allocations(self, ids: list[ObjectID]) -> list[AllocationType]:  # type: ignore
        request = [ReadAllocation(_id=id) for id in ids]
        response = await self._allocation_service.read_many(request)

        return [domain_to_allocation(obj) for obj in response]

    async def __load_form_fields(self, ids: list[ObjectID]) -> list[FormFieldType]:  # type: ignore
        request = [ReadFormField(_id=id) for id in ids]
        response = await self._form_field_service.read_many(request)

        return [domain_to_form_field(obj) for obj in response]

    async def __load_participants(self, ids: list[ObjectID]) -> list[ParticipantType]:  # type: ignore
        request = [ReadParticipant(_id=id) for id in ids]
        response = await self._participant_service.read_many(request)

        return [domain_to_participant(obj) for obj in response]

    async def __load_preferences(self, ids: list[ObjectID]) -> list[PreferenceType]:
        request = [ReadPreference(_id=id) for id in ids]
        response = await self._preference_service.read_many(request)

        return [PreferenceType.from_pydantic(obj) for obj in response]

    async def __load_rooms(self, ids: list[ObjectID]) -> list[RoomType]:
        request = [ReadRoom(_id=id) for id in ids]
        response = await self._room_service.read_many(request)

        return [RoomType.from_pydantic(obj) for obj in response]
