import ujson
from aiohttp import web

from src.protocol.internal.database.user import ReadUser
from src.service.answer import AnswerService
from src.service.participant import ParticipantService
from src.service.user import UserService
from src.utils.logger.logger import Logger

log = Logger("dataset-router")


class DatasetRouter:
    _user_form_redirect_url: str

    def __init__(
        self,
        secret_key: str,
        answer_service: AnswerService,
        participant_service: ParticipantService,
        user_service: UserService,
    ):
        self._secret_key = secret_key
        self._answer_service = answer_service
        self._participant_service = participant_service
        self._user_service = user_service

    def regiter_routers(self, app: web.Application):
        app.add_routes(
            [
                web.get(
                    "/private/dataset/answers",
                    self.answer_handler,
                    name="dataset_answers_router",
                ),
                web.get(
                    "/private/dataset/participants",
                    self.participants_handler,
                    name="dataset_participants_router",
                ),
            ]
        )

    async def answer_handler(self, request: web.Request) -> web.Response:
        secret_key = request.headers.get("X-Secret-Key")
        if secret_key is None or secret_key != self._secret_key:
            log.error("invalid secret key")
            return web.Response(status=403)

        try:
            answers = await self._answer_service.read_all()

            response = web.StreamResponse(
                status=200,
                reason="OK",
                headers={"Content-Type": "application/json"},
            )
            await response.prepare(request)

            await response.write(b"[")
            for i, answer in enumerate(answers):
                data = answer.model_dump(mode="json")

                # TODO: recommendational models do not support multiple option_indexes
                data["option_indexes"] = data["option_indexes"][0]

                await response.write(ujson.dumps(data, ensure_ascii=False).encode())

                if i != len(answers) - 1:
                    await response.write(b",")

            await response.write(b"]")
            await response.write_eof()
            return response  # type: ignore
        except Exception as e:
            return web.Response(status=500, text=str(e))

    async def participants_handler(self, request: web.Request) -> web.Response:
        secret_key = request.headers.get("X-Secret-Key")
        if secret_key is None or secret_key != self._secret_key:
            log.error("invalid secret key")
            return web.Response(status=403)

        try:
            participants = await self._participant_service.read_all()
            user_read_request = [
                ReadUser(_id=participant.user_id) for participant in participants
            ]
            users = await self._user_service.read_many(user_read_request)

            response = web.StreamResponse(
                status=200,
                reason="OK",
                headers={"Content-Type": "application/json"},
            )
            await response.prepare(request)

            await response.write(b"[")

            for user_idx, participant in enumerate(participants):
                data = participant.model_dump(mode="json")
                data["gender"] = users[user_idx].profile.gender

                await response.write(ujson.dumps(data, ensure_ascii=False).encode())

                if user_idx != len(participants) - 1:
                    await response.write(b",")

            await response.write(b"]")
            await response.write_eof()
            return response  # type: ignore
        except Exception as e:
            return web.Response(status=500, text=str(e))
