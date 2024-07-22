import os

from dotenv import load_dotenv

from src.adapter.external.auth.telegram import TgOauthContainer, TgOauthDTO
from src.domain.model.scalar.object_id import ObjectID

load_dotenv()

jwt_secret = os.getenv("JWT_SECRET")
assert jwt_secret is not None


dto = TgOauthDTO(id=ObjectID("669d90fa55df5710d2d9624c"), telegram_id=9536)

print(TgOauthContainer.construct(dto, jwt_secret).to_string())
