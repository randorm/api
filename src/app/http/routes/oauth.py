import json

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


class UserCheckDTO(BaseModel):
    id: int


class OAuthRouter:
    _user_form_redirect_url: str

    def __init__(
        self,
        user_form_redirect_url: str,
        user_profile_redirect_url: str,
        oauth_adapter: OauthProtocol,
        service: UserService,
    ):
        self._user_form_redirect_url = user_form_redirect_url
        self._user_profile_redirect_url = user_profile_redirect_url
        self._oauth_adapter = oauth_adapter
        self._service = service

    def regiter_routers(self, app: web.Application):
        app.add_routes(
            [
                web.get(
                    "/oauth/telegram/callback",
                    self.callback_handler,
                    name="oauth_callback",
                ),
                web.get(
                    "/oauth/telegram/register",
                    self.register_handler,
                    name="oauth_register",
                ),
                web.get(
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
        try:
            payload = request.query

            container = await self._oauth_adapter.login(payload)
        except UserNotFoundException:
            return web.Response(
                status=302, headers={"Location": self._user_form_redirect_url}
            )

        return web.Response(
            status=302,
            headers={
                "Location": self._user_profile_redirect_url,
                "Set-Cookie": f"AccessToken={container.to_string()}; HttpOnly",
            },
        )

    async def register_handler(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()

            container = await self._oauth_adapter.register(payload)
        except UserAlreadyExistsException:
            return web.Response(
                status=409, text=json.dumps({"msg": "user already exists"})
            )
        except AuthException as e:
            return web.Response(status=400, text=json.dumps({"msg": str(e)}))

        return web.Response(
            status=200,
            headers={
                "Location": self._user_profile_redirect_url,
                "Set-Cookie": f"AccessToken={container.to_string()}; HttpOnly",
            },
        )

    async def login_handler(self, request: web.Request) -> web.Response:
        try:
            payload = await request.json()

            container = await self._oauth_adapter.login(payload)
        except UserNotFoundException:
            return web.Response(status=404, text=json.dumps({"msg": "user not found"}))
        except AuthException as e:
            return web.Response(status=400, text=json.dumps({"msg": str(e)}))

        return web.Response(
            status=200,
            headers={
                "Location": self._user_profile_redirect_url,
                "Set-Cookie": f"AccessToken={container.to_string()}; HttpOnly",
            },
        )
