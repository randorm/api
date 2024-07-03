import os

from aiohttp import web
from dotenv import load_dotenv

from src.adapter.external.auth.telegram import TelegramOauthAdapter
from src.adapter.internal.memorydb.service import MemoryDBAdapter
from src.app.http.routes import oauth
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

    oauth_adapter = TelegramOauthAdapter(secret_token, jwt_secret, user_service)

    oauth.OAuthRouter(
        user_form_redirect_url="http://localhost:8080/user/form",
        user_profile_redirect_url="http://localhost:8080/user/profile",
        oauth_adapter=oauth_adapter,
        service=user_service,
    ).regiter_routers(app)

    return app
