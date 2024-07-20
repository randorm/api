from aiohttp import web

from src.adapter.external.graphql.view import GRAPHQL_SCHEMA, RandormGraphQLView
from src.app.http.routes import oauth
from src.protocol.external.auth.oauth import OauthProtocol
from src.service.allocation import AllocationService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService


def build_server(
    user_service: UserService,
    allocation_service: AllocationService,
    form_field_service: FormFieldService,
    participant_service: ParticipantService,
    preference_service: PreferenceService,
    room_service: RoomService,
    oauth_adapter: OauthProtocol,
):
    app = web.Application()

    oauth.OAuthRouter(
        user_form_redirect_url="http://localhost:8080/user/form",
        user_profile_redirect_url="http://localhost:8080/user/profile",
        oauth_adapter=oauth_adapter,
        service=user_service,
    ).regiter_routers(app)

    app.router.add_route(
        "*",
        "/graphql",
        RandormGraphQLView(
            GRAPHQL_SCHEMA,
            user_service,
            allocation_service,
            form_field_service,
            participant_service,
            preference_service,
            room_service,
        ),
    )

    return app
