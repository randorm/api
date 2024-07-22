import os

import rich
from dotenv import load_dotenv

from src.adapter.external.auth.telegram import TelegramOauthAdapter

# from src.adapter.internal.database.memorydb.service import MemoryDBAdapter
from src.adapter.internal.database.mongodb.service import MongoDBAdapter
from src.app.http.server import build_server
from src.service.allocation import AllocationService
from src.service.answer import AnswerService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService


async def app():
    load_dotenv()

    telegram_token = os.getenv("TELEGRAM_TOKEN")
    if telegram_token is None:
        raise RuntimeError("TELEGRAM_TOKEN is not set")

    telegram_secret = os.getenv("TELEGRAM_SECRET")
    if telegram_secret is None:
        raise RuntimeError("TELEGRAM_SECRET is not set")

    jwt_secret = os.getenv("JWT_SECRET")
    if jwt_secret is None:
        raise RuntimeError("JWT_SECRET is not set")

    service_secret_key = os.getenv("SERVICE_SECRET_KEY")
    if service_secret_key is None:
        raise RuntimeError("SERVICE_SECRET_KEY is not set")

    base_url = os.getenv("BASE_URL")
    if base_url is None:
        raise RuntimeError("BASE_URL is not set")

    redis_dsn = os.getenv("REDIS_DSN")
    if redis_dsn is None:
        raise RuntimeError("REDIS_DSN is not set")

    mongo_dsn = os.getenv("MONGO_DSN")
    if mongo_dsn is None:
        raise RuntimeError("MONGO_DSN is not set")

    telegram_webhook_url = os.getenv("TELEGRAM_WEBHOOK_URL")
    if telegram_webhook_url is None:
        raise RuntimeError("TELEGRAM_WEBHOOK_URL is not set")

    repo = await MongoDBAdapter.create(mongo_dsn)
    user_service = UserService(repo)

    allocation_service = AllocationService(
        allocation_repo=repo,
        form_field_repo=repo,
        participant_repo=repo,
        user_repo=repo,
    )
    form_field_service = FormFieldService(
        allocation_repo=repo,
        form_field_repo=repo,
        user_repo=repo,
    )
    participant_service = ParticipantService(
        allocatin_repo=repo,
        participant_repo=repo,
        room_repo=repo,
        user_repo=repo,
    )
    preference_service = PreferenceService(
        preference_repo=repo,
        user_repo=repo,
    )
    room_service = RoomService(
        room_repo=repo,
        user_repo=repo,
    )
    answer_service = AnswerService(
        form_field_repo=repo,
        participant_repo=repo,
    )

    oauth_adapter = TelegramOauthAdapter(telegram_token, jwt_secret, user_service)

    return build_server(
        telegram_token=telegram_token,
        telegram_secret=telegram_secret,
        webhook_url=telegram_webhook_url,
        redis_dsn=redis_dsn,
        register_url=base_url + "/register",
        fallback_url=base_url,
        service_secret_key=service_secret_key,
        user_service=user_service,
        answer_service=answer_service,
        allocation_service=allocation_service,
        form_field_service=form_field_service,
        participant_service=participant_service,
        preference_service=preference_service,
        room_service=room_service,
        oauth_adapter=oauth_adapter,
    )


if __name__ == "__main__":
    rich.print(
        "You should run",
        (
            "\t[bold yellow]"
            "python3 -m gunicorn main:app --bind 0.0.0.0:8080 --worker-class aiohttp.GunicornWebWorker"
            "[/bold yellow]"
        ),
        "to start the server",
        sep="\n",
    )
