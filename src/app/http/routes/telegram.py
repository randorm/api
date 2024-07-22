from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web


class TelegramRouter:
    def __init__(self, bot: Bot, dispatcher: Dispatcher, webhook_secret: str):
        self._bot = bot
        self._dispatcher = dispatcher
        self._webhook_secret = webhook_secret

    def regiter_routers(self, app: web.Application):
        handler = SimpleRequestHandler(
            dispatcher=self._dispatcher,
            bot=self._bot,
            secret_token=self._webhook_secret,
        )

        handler.register(app, path="/telegram/webhook")
        setup_application(app, self._dispatcher, bot=self._bot)
