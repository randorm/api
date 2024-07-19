import os

from aiohttp import web
from aiohttp_asgi import ASGIResource
from dotenv import load_dotenv

from src.adapter.external.auth.telegram import TelegramOauthAdapter
from src.adapter.external.graphql.view import GRAPHQL_SCHEMA, RandormGraphQL
from src.adapter.internal.database.memorydb.service import MemoryDBAdapter
from src.app.http.routes import oauth
from src.service.allocation import AllocationService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService


def init(argv):
    load_dotenv()

    app = web.Application()

    secret_token = os.getenv("SECRET_TOKEN")
    if secret_token is None:
        raise RuntimeError("SECRET_TOKEN is not set")

    jwt_secret = os.getenv("JWT_SECRET")
    if jwt_secret is None:
        raise RuntimeError("JWT_SECRET is not set")

    repo = MemoryDBAdapter()
    user_service = UserService(repo)
    allocation_service = AllocationService(repo)
    form_field_service = FormFieldService(repo)
    participant_service = ParticipantService(repo)
    preference_service = PreferenceService(repo)
    room_service = RoomService(repo)

    oauth_adapter = TelegramOauthAdapter(secret_token, jwt_secret, user_service)

    oauth.OAuthRouter(
        user_form_redirect_url="http://localhost:8080/user/form",
        user_profile_redirect_url="http://localhost:8080/user/profile",
        oauth_adapter=oauth_adapter,
        service=user_service,
    ).regiter_routers(app)

    graphql_resource = ASGIResource(
        RandormGraphQL(
            GRAPHQL_SCHEMA,
            user_service,
            allocation_service,
            form_field_service,
            participant_service,
            preference_service,
            room_service,
        ),
        root_path="/graphql",
    )

    app.router.register_resource(graphql_resource)

    return app
