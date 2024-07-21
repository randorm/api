from aiohttp import web

from src.adapter.external.graphql.schema import SCHEMA
from src.adapter.external.graphql.view import RandormGraphQLView
from src.app.http.routes import dataset, oauth
from src.protocol.external.auth.oauth import OauthProtocol
from src.service.allocation import AllocationService
from src.service.answer import AnswerService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService


def build_server(
    base_url: str,
    service_secret_key: str,
    user_service: UserService,
    answer_service: AnswerService,
    allocation_service: AllocationService,
    form_field_service: FormFieldService,
    participant_service: ParticipantService,
    preference_service: PreferenceService,
    room_service: RoomService,
    oauth_adapter: OauthProtocol,
):
    app = web.Application()

    oauth.OAuthRouter(
        user_form_redirect_url=f"{base_url}/form",
        user_profile_redirect_url=f"{base_url}/profile",
        oauth_adapter=oauth_adapter,
        service=user_service,
    ).regiter_routers(app)

    dataset.DatasetRouter(
        secret_key=service_secret_key,
        answer_service=answer_service,
        user_service=user_service,
        participant_service=participant_service,
    ).regiter_routers(app)

    app.router.add_route(
        "*",
        "/graphql",
        RandormGraphQLView(
            SCHEMA,
            user_service,
            allocation_service,
            form_field_service,
            answer_service,
            participant_service,
            preference_service,
            room_service,
        ),
    )

    return app
