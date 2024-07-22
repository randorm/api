import ujson
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from src.app.http.telegram.info import Services, TelegramInfo
from src.app.http.telegram.routers import router
from src.service.allocation import AllocationService
from src.service.answer import AnswerService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService
from src.utils.logger.logger import Logger

log = Logger("telegram-router")


def startup_hook_factory(webhook_url: str, webhook_secret: str):
    async def startup_hook(bot: Bot):
        with log.activity("startup_hook"):
            log.info("set telegram webhook to {}", webhook_url + "/telegram/webhook")
            await bot.set_webhook(
                webhook_url + "/telegram/webhook", secret_token=webhook_secret
            )

    return startup_hook


def shutdown_hook_factory():
    async def shutdown_hook(bot: Bot):
        with log.activity("shutdown_hook"):
            log.info("delete telegram webhook")
            await bot.delete_webhook()

    return shutdown_hook


class Telegram:
    def __init__(
        self,
        token: str,
        secret: str,
        redis_dsn: str,
        webhook_url: str,
        user_service: UserService,
        answer_service: AnswerService,
        allocation_service: AllocationService,
        form_field_service: FormFieldService,
        participant_service: ParticipantService,
        preference_service: PreferenceService,
        room_service: RoomService,
    ):
        self._token = token
        self._secret = secret

        self._dp = Dispatcher(
            storage=RedisStorage(
                Redis.from_url(redis_dsn),
                json_loads=ujson.loads,
                json_dumps=ujson.dumps,
            ),
            info=TelegramInfo(
                srv=Services(
                    allocation=allocation_service,
                    answer=answer_service,
                    form_field=form_field_service,
                    participant=participant_service,
                    preference=preference_service,
                    room=room_service,
                    user=user_service,
                )
            ),
        )

        self._dp.include_router(router)

        self._bot = Bot(
            token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )

        self._dp.startup.register(startup_hook_factory(webhook_url, self._secret))
        self._dp.shutdown.register(shutdown_hook_factory())

    @property
    def dispatcher(self) -> Dispatcher:
        return self._dp

    @property
    def bot(self) -> Bot:
        return self._bot
