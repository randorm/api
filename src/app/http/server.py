from aiohttp import web

from src.adapter.external.graphql.schema import SCHEMA
from src.adapter.external.graphql.view import RandormGraphQLView
from src.app.http.routes import dataset, oauth
from src.app.http.routes.telegram import TelegramRouter
from src.app.http.telegram.bot import Telegram
from src.protocol.external.auth.oauth import OauthProtocol
from src.service.allocation import AllocationService
from src.service.answer import AnswerService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService


def build_server(
    register_url: str,
    fallback_url: str,
    webhook_url: str,
    service_secret_key: str,
    telegram_token: str,
    telegram_secret: str,
    redis_dsn: str,
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
        register_url=register_url,
        fallback_url=fallback_url,
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
        method="*",
        path="/graphql",
        handler=RandormGraphQLView(
            schema=SCHEMA,
            user_service=user_service,
            allocation_service=allocation_service,
            form_field_service=form_field_service,
            answer_service=answer_service,
            participant_service=participant_service,
            preference_service=preference_service,
            room_service=room_service,
        ),
    )

    tg = Telegram(
        token=telegram_token,
        secret=telegram_secret,
        redis_dsn=redis_dsn,
        webhook_url=webhook_url,
        user_service=user_service,
        answer_service=answer_service,
        allocation_service=allocation_service,
        form_field_service=form_field_service,
        participant_service=participant_service,
        preference_service=preference_service,
        room_service=room_service,
    )

    TelegramRouter(
        tg.bot,
        tg.dispatcher,
        telegram_secret,
    ).regiter_routers(app)

    return app
