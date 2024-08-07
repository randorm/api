import strawberry as sb
import ujson
from strawberry.aiohttp.views import GraphQLView
from strawberry.dataloader import DataLoader, DefaultCache
from strawberry.http import GraphQLHTTPResponse

from src.adapter.external.auth.telegram import TgOauthContainer
from src.adapter.external.graphql.tool.context import Context, DataContext
from src.adapter.external.graphql.type.allocation import (
    BaseAllocationType,
    domain_to_allocation,
)
from src.adapter.external.graphql.type.form_field import (
    BaseAnswerType,
    BaseFormFieldType,
    domain_to_answer,
    domain_to_form_field,
)
from src.adapter.external.graphql.type.participant import (
    BaseParticipantType,
    domain_to_participant,
)
from src.adapter.external.graphql.type.preference import PreferenceType
from src.adapter.external.graphql.type.room import RoomType
from src.adapter.external.graphql.type.user import UserType
from src.domain.model.scalar.object_id import ObjectID
from src.protocol.external.auth.oauth import OauthProtocol
from src.protocol.internal.database.allocation import ReadAllocation
from src.protocol.internal.database.form_field import ReadAnswer, ReadFormField
from src.protocol.internal.database.participant import ReadParticipant
from src.protocol.internal.database.preference import ReadPreference
from src.protocol.internal.database.room import ReadRoom
from src.protocol.internal.database.user import ReadUser
from src.service.allocation import AllocationService
from src.service.answer import AnswerService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService
from src.utils.logger.logger import Logger

log = Logger("graphql-view")


class CustomDefaultCache[K, T](DefaultCache[K, T]):
    def delete(self, key: K) -> None:
        if key in self.cache_map:
            del self.cache_map[key]


class RandormGraphQLView(GraphQLView):
    def __init__(
        self,
        schema: sb.Schema,
        oauth_adapter: OauthProtocol,
        user_service: UserService,
        allocation_service: AllocationService,
        form_field_service: FormFieldService,
        answer_service: AnswerService,
        participant_service: ParticipantService,
        preference_service: PreferenceService,
        room_service: RoomService,
    ):
        self._oauth_adapter = oauth_adapter
        self._user_service = user_service
        self._allocation_service = allocation_service
        self._form_field_service = form_field_service
        self._answer_service = answer_service
        self._participant_service = participant_service
        self._preference_service = preference_service
        self._room_service = room_service
        super().__init__(schema, debug=False)

    async def get_context(self, request, response):
        token = request.headers.get("Authorization")
        if not token:
            token = request.cookies.get("AccessToken")

        if token:
            log.debug(f"token {token}")
            dto = TgOauthContainer(jwt=token).to_dto(self._oauth_adapter._jwt_secret)  # type: ignore
            log.debug(dto)
        else:
            dto = None

        return Context(
            user_id=dto.id if dto else None,
            telegram_id=dto.telegram_id if dto else None,
            request=request,
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
            answer=DataContext(
                loader=DataLoader(
                    load_fn=self.__load_answers,
                    cache_key_fn=str,
                    cache_map=CustomDefaultCache(),
                ),
                service=self._answer_service,
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

    async def __load_answers(self, ids: list[ObjectID]) -> list[BaseAnswerType]:
        request = [ReadAnswer(_id=id) for id in ids]
        response = await self._answer_service.read_many(request)

        return [domain_to_answer(obj) for obj in response]

    async def __load_allocations(self, ids: list[ObjectID]) -> list[BaseAllocationType]:
        request = [ReadAllocation(_id=id) for id in ids]
        response = await self._allocation_service.read_many(request)

        return [domain_to_allocation(obj) for obj in response]

    async def __load_form_fields(self, ids: list[ObjectID]) -> list[BaseFormFieldType]:
        request = [ReadFormField(_id=id) for id in ids]
        response = await self._form_field_service.read_many(request)

        return [domain_to_form_field(obj) for obj in response]

    async def __load_participants(
        self, ids: list[ObjectID]
    ) -> list[BaseParticipantType]:
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

    def encode_json(self, response_data: GraphQLHTTPResponse) -> str:
        return ujson.dumps(response_data, ensure_ascii=False)
