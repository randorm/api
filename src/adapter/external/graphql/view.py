import strawberry as sb
from strawberry.asgi import GraphQL
from strawberry.dataloader import DataLoader

from src.adapter.external.graphql.query import GRAPHQL_QUERY
from src.adapter.external.graphql.tool.context import Context, DataContext
from src.adapter.external.graphql.type.allocation import AllocationType
from src.adapter.external.graphql.type.form_field import FormFieldType
from src.adapter.external.graphql.type.participant import ParticipantType
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

GRAPHQL_SCHEMA = sb.Schema(query=GRAPHQL_QUERY)


class RandormGraphQL(GraphQL):
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
                loader=DataLoader(load_fn=self.__load_users),
                service=self._user_service,
            ),
            allocation=DataContext(
                loader=DataLoader(load_fn=self.__load_allocations),
                service=self._allocation_service,
            ),
            form_field=DataContext(
                loader=DataLoader(load_fn=self.__load_form_fields),
                service=self._form_field_service,
            ),
            participant=DataContext(
                loader=DataLoader(load_fn=self.__load_participants),
                service=self._participant_service,
            ),
            preference=DataContext(
                loader=DataLoader(load_fn=self.__load_preferences),
                service=self._preference_service,
            ),
            room=DataContext(
                loader=DataLoader(load_fn=self.__load_rooms),
                service=self._room_service,
            ),
        )

    async def __load_users(self, ids: list[ObjectID]) -> list[UserType]:
        return [
            UserType.from_pydantic(await self._user_service.read(ReadUser(_id=id)))
            for id in ids
        ]

    async def __load_allocations(self, ids: list[ObjectID]) -> list[AllocationType]:
        return [
            AllocationType.from_pydantic(
                await self._allocation_service.read(ReadAllocation(_id=id))
            )
            for id in ids
        ]

    async def __load_form_fields(self, ids: list[ObjectID]) -> list[FormFieldType]:
        return [
            FormFieldType.from_pydantic(
                await self._form_field_service.read(ReadFormField(_id=id))
            )
            for id in ids
        ]

    async def __load_participants(self, ids: list[ObjectID]) -> list[ParticipantType]:
        return [
            ParticipantType.from_pydantic(
                await self._participant_service.read(ReadParticipant(_id=id))
            )
            for id in ids
        ]

    async def __load_preferences(self, ids: list[ObjectID]) -> list[PreferenceType]:
        return [
            PreferenceType.from_pydantic(
                await self._preference_service.read(ReadPreference(_id=id))
            )
            for id in ids
        ]

    async def __load_rooms(self, ids: list[ObjectID]) -> list[RoomType]:
        return [
            RoomType.from_pydantic(await self._room_service.read(ReadRoom(_id=id)))
            for id in ids
        ]
