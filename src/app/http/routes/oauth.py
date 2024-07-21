from collections import OrderedDict
from urllib.parse import urlencode

import ujson
from aiohttp import web
from pydantic import BaseModel

from src.app.http.common import CORS_HEADERS
from src.domain.exception.auth import (
    AuthException,
    UserAlreadyExistsException,
    UserNotFoundException,
)
from src.protocol.external.auth.oauth import OauthProtocol
from src.service.user import UserService
from src.utils.logger.logger import Logger

log = Logger("oauth-router")


class UserCheckDTO(BaseModel):
    id: int


class OAuthRouter:
    _user_form_redirect_url: str

    def __init__(
        self,
        register_url: str,
        fallback_url: str,
        oauth_adapter: OauthProtocol,
        service: UserService,
    ):
        self._register_url = register_url
        self._fallback_url = fallback_url
        self._oauth_adapter = oauth_adapter
        self._service = service

        self._exclude_query_keys = [
            "redirect_url",
            "hash",
            "id",
            "auth_date",
            "first_name",
            "last_name",
            "username",
            "photo_url",
        ]

    def regiter_routers(self, app: web.Application):
        app.add_routes(
            [
                web.get(
                    "/oauth/telegram/callback",
                    self.callback_handler,
                    name="oauth_callback",
                ),
                web.post(
                    "/oauth/telegram/register",
                    self.register_handler,
                    name="oauth_register",
                ),
                web.post(
                    "/oauth/telegram/login",
                    self.login_handler,
                    name="oauth_login",
                ),
                web.options(
                    "/oauth/telegram/callback",
                    self.options_handler,
                    name="oauth_callback_router",
                ),
                web.options(
                    "/oauth/telegram/register",
                    self.options_handler,
                    name="oauth_register_router",
                ),
                web.options(
                    "/oauth/telegram/login",
                    self.options_handler,
                    name="oauth_login_router",
                ),
            ]
        )

    async def options_handler(self, request: web.Request) -> web.Response:
        return web.Response(status=200, text="OK", headers=CORS_HEADERS)

    async def callback_handler(self, request: web.Request) -> web.Response:
        with log.activity("callback_handler"):
            try:
                payload = request.query

                container = await self._oauth_adapter.login(payload)
            except UserNotFoundException:
                return web.Response(
                    status=302,
                    headers={
                        "Location": self._register_url + "?" + request.query_string
                    },
                )
            except Exception as e:
                log.error("failed to login user with exception: {}", e)
                return web.Response(status=403, text="Callback data is malformed")

            location = self._build_location(request.query)
            return web.Response(
                status=302,
                headers={
                    "Location": location,
                    "Set-Cookie": f"AccessToken={container.to_string()}; HttpOnly",
                },
            )

    async def register_handler(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()

            container = await self._oauth_adapter.register(payload)
        except UserAlreadyExistsException:
            return web.Response(
                status=409, text=ujson.dumps({"msg": "user already exists"})
            )
        except AuthException as e:
            return web.Response(status=400, text=ujson.dumps({"msg": str(e)}))

        return web.Response(
            status=200,
            headers={
                "Location": self._build_location(request.query),
                "Set-Cookie": f"AccessToken={container.to_string()}; HttpOnly",
            },
        )

    async def login_handler(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()

            container = await self._oauth_adapter.login(payload)
        except UserNotFoundException:
            return web.Response(status=404, text=ujson.dumps({"msg": "user not found"}))
        except AuthException as e:
            return web.Response(status=400, text=ujson.dumps({"msg": str(e)}))

        return web.Response(
            status=200,
            headers={
                "Location": self._build_location(request.query),
                "Set-Cookie": f"AccessToken={container.to_string()}; HttpOnly",
            },
        )

    def _build_location(self, query):
        redirect_url = query.get("redirect_url", self._fallback_url)

        query_data = OrderedDict()
        for key, value in query.items():
            if key in self._exclude_query_keys:
                continue

            query_data[key] = value
        location = redirect_url + "?" + urlencode(query_data)
        return location
