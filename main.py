import os

import rich
from dotenv import load_dotenv

from src.adapter.external.auth.telegram import TelegramOauthAdapter
from src.adapter.internal.database.memorydb.service import MemoryDBAdapter
from src.app.http.server import build_server
from src.service.allocation import AllocationService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService


async def app():
    load_dotenv()

    # repo = await MongoDBAdapter.create("mongodb://localhost:27017/randorm")
    repo = MemoryDBAdapter()

    secret_token = os.getenv("SECRET_TOKEN")
    if secret_token is None:
        raise RuntimeError("SECRET_TOKEN is not set")

    jwt_secret = os.getenv("JWT_SECRET")
    if jwt_secret is None:
        raise RuntimeError("JWT_SECRET is not set")

    user_service = UserService(repo)
    allocation_service = AllocationService(repo)
    form_field_service = FormFieldService(repo)
    participant_service = ParticipantService(repo)
    preference_service = PreferenceService(repo)
    room_service = RoomService(repo)

    oauth_adapter = TelegramOauthAdapter(secret_token, jwt_secret, user_service)

    return build_server(
        user_service,
        allocation_service,
        form_field_service,
        participant_service,
        preference_service,
        room_service,
        oauth_adapter,
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
