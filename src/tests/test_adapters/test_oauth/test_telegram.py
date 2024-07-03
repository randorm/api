import hashlib
import hmac
import json
import secrets
from datetime import date, datetime

import pytest
from pydantic import BaseModel

import src.domain.exception.auth as exception
import src.protocol.external.auth as proto
from src.adapter.external.auth.telegram import (
    TelegramAuthCallback,
    TelegramOauthAdapter,
    TelegramOauthContainer,
    TelegramUserProfileMixin,
)
from src.adapter.internal.memorydb.service import MemoryDBAdapter
from src.domain.model.scalar.object_id import ObjectID
from src.domain.model.user import Gender, LanguageCode
from src.protocol.internal.database.user import ReadUser
from src.service.user.create import CreateUserService

secret_token = secrets.token_hex(32)


async def _get_telegram_oauth(
    storage: MemoryDBAdapter | None = None,
) -> proto.OauthProtocol:
    if storage is None:
        storage = MemoryDBAdapter()

    return TelegramOauthAdapter(secret_token, CreateUserService(storage))


async def test_verify_callback_data_ok():
    storage = MemoryDBAdapter()
    actor = await _get_telegram_oauth(storage)

    payload = TelegramAuthCallback(
        id=123456789,
        auth_date=datetime.now().replace(microsecond=0),
        first_name="John",
        last_name="Doe",
        username="johndoe",
        photo_url="https://example.com/photo.jpg",
        profile=TelegramUserProfileMixin(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            birthdate=datetime.today().date(),
            language_code=LanguageCode.RU,
            gender=Gender.MALE,
        ),
        hash="",
    )

    signing = hmac.new(
        secret_token.encode(), payload.to_data_string().encode(), hashlib.sha256
    )
    payload.hash = signing.hexdigest()

    container = await actor.verify_callback_data(payload)

    assert isinstance(container, TelegramOauthContainer)
    assert isinstance(container.id, ObjectID)
    assert container.tid == payload.id

    user = await storage.read_user(ReadUser(_id=container.id))
    assert user.tid == payload.id
    assert user.profile.first_name == payload.profile.first_name
    assert user.profile.last_name == payload.profile.last_name
    assert user.profile.username == payload.profile.username
    assert user.profile.birthdate == payload.profile.birthdate
    assert user.profile.language_code == payload.profile.language_code
    assert user.profile.gender == payload.profile.gender


async def test_verify_callback_data__from_dict_ok():
    storage = MemoryDBAdapter()
    actor = await _get_telegram_oauth(storage)

    payload = TelegramAuthCallback(
        id=123456789,
        auth_date=datetime.now().replace(microsecond=0),
        first_name="John",
        last_name="Doe",
        username="johndoe",
        photo_url="https://example.com/photo.jpg",
        profile=TelegramUserProfileMixin(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            birthdate=datetime.today().date(),
            language_code=LanguageCode.RU,
            gender=Gender.MALE,
        ),
        hash="",
    )

    signing = hmac.new(
        secret_token.encode(), payload.to_data_string().encode(), hashlib.sha256
    )
    payload.hash = signing.hexdigest()

    payload_data = json.loads(payload.model_dump_json())

    container = await actor.verify_callback_data(payload_data)

    assert isinstance(container, TelegramOauthContainer)
    assert isinstance(container.id, ObjectID)
    assert container.tid == payload.id

    user = await storage.read_user(ReadUser(_id=container.id))
    assert user.tid == payload.id
    assert user.profile.first_name == payload.profile.first_name
    assert user.profile.last_name == payload.profile.last_name
    assert user.profile.username == payload.profile.username
    assert user.profile.birthdate == payload.profile.birthdate
    assert user.profile.language_code == payload.profile.language_code
    assert user.profile.gender == payload.profile.gender


async def test_verify_callback_data_invalid_input_data_error():
    actor = await _get_telegram_oauth()

    # missing a lot of fields
    payload_data = {
        "first_name": "John",
        "last_name": "Doe",
        "username": "johndoe",
    }

    with pytest.raises(exception.InvalidCredentialsException):
        await actor.verify_callback_data(payload_data)


async def test_verify_callback_data_hash_mismatch_error():
    actor = await _get_telegram_oauth()

    payload = TelegramAuthCallback(
        id=123456789,
        auth_date=datetime.now().replace(microsecond=0),
        first_name="John",
        last_name="Doe",
        username="johndoe",
        photo_url="https://example.com/photo.jpg",
        profile=TelegramUserProfileMixin(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            birthdate=datetime.today().date(),
            language_code=LanguageCode.RU,
            gender=Gender.MALE,
        ),
        hash="",
    )

    signing = hmac.new(
        secret_token.encode(), payload.to_data_string().encode(), hashlib.sha256
    )

    payload.hash = signing.hexdigest()
    payload.last_name = "XXX"  # data is malformed

    with pytest.raises(exception.InvalidCredentialsException):
        await actor.verify_callback_data(payload)


async def test_verify_callback_data_reflect_error():
    actor = await _get_telegram_oauth()

    payload = TelegramAuthCallback(
        id=123456789,
        auth_date=datetime.now().replace(microsecond=0),
        first_name="John",
        last_name="Doe",
        username="johndoe",
        photo_url="https://example.com/photo.jpg",
        profile=TelegramUserProfileMixin(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            birthdate=datetime.today().date(),
            language_code=LanguageCode.RU,
            gender=Gender.MALE,
        ),
        hash="",
    )

    class InvalidProfile(BaseModel):
        # missing fields
        first_name: str
        last_name: str
        birthdate: date

    signing = hmac.new(
        secret_token.encode(), payload.to_data_string().encode(), hashlib.sha256
    )
    payload.hash = signing.hexdigest()
    payload.profile = InvalidProfile(
        first_name="John", last_name="Doe", birthdate=date.today()
    )  # type: ignore

    with pytest.raises(exception.InvalidCredentialsException):
        await actor.verify_callback_data(payload)


async def test_verify_callback_data_user_exists_error():
    storage = MemoryDBAdapter()
    actor = await _get_telegram_oauth(storage)

    payload = TelegramAuthCallback(
        id=123456789,
        auth_date=datetime.now().replace(microsecond=0),
        first_name="John",
        last_name="Doe",
        username="johndoe",
        photo_url="https://example.com/photo.jpg",
        profile=TelegramUserProfileMixin(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            birthdate=datetime.today().date(),
            language_code=LanguageCode.RU,
            gender=Gender.MALE,
        ),
        hash="",
    )

    signing = hmac.new(
        secret_token.encode(), payload.to_data_string().encode(), hashlib.sha256
    )
    payload.hash = signing.hexdigest()

    payload_data = json.loads(payload.model_dump_json())

    container = await actor.verify_callback_data(payload_data)

    assert isinstance(container, TelegramOauthContainer)
    assert isinstance(container.id, ObjectID)
    assert container.tid == payload.id

    user = await storage.read_user(ReadUser(_id=container.id))
    assert user.tid == payload.id
    assert user.profile.first_name == payload.profile.first_name
    assert user.profile.last_name == payload.profile.last_name
    assert user.profile.username == payload.profile.username
    assert user.profile.birthdate == payload.profile.birthdate
    assert user.profile.language_code == payload.profile.language_code
    assert user.profile.gender == payload.profile.gender

    # creating the same useg again result in an error
    with pytest.raises(exception.UserAlreadyExistsException):
        await actor.verify_callback_data(payload)


async def test_retrieve_user_ok():
    actor = await _get_telegram_oauth()

    payload = TelegramAuthCallback(
        id=123456789,
        auth_date=datetime.now().replace(microsecond=0),
        first_name="John",
        last_name="Doe",
        username="johndoe",
        photo_url="https://example.com/photo.jpg",
        profile=TelegramUserProfileMixin(
            first_name="John",
            last_name="Doe",
            username="johndoe",
            birthdate=datetime.today().date(),
            language_code=LanguageCode.RU,
            gender=Gender.MALE,
        ),
        hash="",
    )

    signing = hmac.new(
        secret_token.encode(), payload.to_data_string().encode(), hashlib.sha256
    )
    payload.hash = signing.hexdigest()

    container = await actor.verify_callback_data(payload)

    user = await actor.retrieve_user(container)

    assert user.tid == payload.id
    assert user.profile.first_name == payload.profile.first_name
    assert user.profile.last_name == payload.profile.last_name
    assert user.profile.username == payload.profile.username
    assert user.profile.birthdate == payload.profile.birthdate
    assert user.profile.language_code == payload.profile.language_code
    assert user.profile.gender == payload.profile.gender


async def test_retrieve_user_invalid_input_data_error():
    actor = await _get_telegram_oauth()

    with pytest.raises(exception.InvalidCredentialsException):
        await actor.retrieve_user(object)  # type: ignore


async def test_retrieve_user_reflect_error():
    actor = await _get_telegram_oauth()

    class InvalidData:
        id: object = object

    with pytest.raises(exception.InvalidCredentialsException):
        await actor.retrieve_user(InvalidData())  # type: ignore


async def test_retrieve_user_not_found_error():
    actor = await _get_telegram_oauth()

    with pytest.raises(exception.UserNotFoundException):
        await actor.retrieve_user(TelegramOauthContainer(id=ObjectID(), tid=0))
