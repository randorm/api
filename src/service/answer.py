import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.service import common
from src.utils.logger.logger import Logger

log = Logger("answer-service")


class AnswerService:
    def __init__(
        self,
        form_field_repo: proto.FormFieldDatabaseProtocol,
        participant_repo: proto.ParticipantDatabaseProtocol,
    ):
        self._form_field_repo = form_field_repo
        self._participant_repo = participant_repo

    async def create(self, answer: proto.CreateAnswer) -> domain.Answer:
        try:
            # todo: check dublicates
            log.debug("checking answer respondent existence")

            log.debug("checking answer form field existence")
            if not await common.check_form_field_exist(answer, self._form_field_repo):
                log.error("form field does not exist")
                raise service_exception.CreateAnswerException(
                    "form field does not exist"
                )

            log.debug("checking answer respondent existence")
            if not await common.check_respondent_exist(answer, self._participant_repo):
                log.error("participant does not exist")
                raise service_exception.CreateAnswerException(
                    "participant does not exist"
                )

            log.debug("reading form field")
            question = await self._form_field_repo.read_form_field(
                proto.ReadFormField(_id=answer.form_field_id)
            )

            if isinstance(answer, proto.CreateChoiceAnswer):
                log.debug("checking answer choice answer")
                self.__check_choice_answer(answer, question)

            if isinstance(answer, proto.CreateTextAnswer):
                log.debug("checking answer text answer")
                self.__check_text_answer(answer, question)

            log.debug("creating new answer")
            return await self._form_field_repo.create_answer(answer)

        except service_exception.ServiceException as e:
            log.error("failed to create answer with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to create answer with error: {}", e)
            raise service_exception.CreateAnswerException(
                "service failed to create answer"
            ) from e

    async def read(self, answer: proto.ReadAnswer) -> domain.Answer:
        try:
            log.debug(f"reading answer {answer.id}")
            return await self._form_field_repo.read_answer(answer)
        except Exception as e:
            log.error("failed to read answer with error: {}", e)
            raise service_exception.ReadAnswerException(
                "service failed to read answer"
            ) from e

    async def update(self, answer: proto.UpdateAnswer) -> domain.Answer:
        try:
            log.debug(f"updating answer {answer.id}")
            try:
                log.debug(f"reading answer {answer.id}")
                current = await self._form_field_repo.read_answer(
                    proto.ReadAnswer(_id=answer.id)
                )
            except Exception as e:
                log.error("failed to read answer with error: {}", e)
                raise service_exception.UpdateAnswerException(
                    "answer does not exist"
                ) from e

            log.debug("checking answer kind change")
            if answer.kind != current.kind:
                log.error("can not change answer type")
                raise service_exception.UpdateAnswerException(
                    "can not change answer type"
                )

            log.debug("checking answer respondent non-updateability")
            if answer.respondent_id is not None:
                log.error("can not change respondent")
                raise service_exception.UpdateAnswerException(
                    "can not change respondent"
                )

            log.debug("checking answer form field non-updateability")
            if answer.form_field_id is not None:
                log.error("can not change form field")
                raise service_exception.UpdateAnswerException(
                    "can not change form field"
                )

            log.debug("reading form field")
            question = await self._form_field_repo.read_form_field(
                proto.ReadFormField(_id=current.form_field_id)
            )

            if isinstance(answer, proto.UpdateChoiceAnswer):
                log.debug("checking answer choice answer")
                self.__check_choice_answer(answer, question)

            if isinstance(answer, proto.UpdateTextAnswer):
                log.debug("checking answer text answer")
                self.__check_text_answer(answer, question)

            log.debug("updating answer")
            return await self._form_field_repo.update_answer(answer)
        except service_exception.ServiceException as e:
            log.error("failed to update answer with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to update answer with error: {}", e)
            raise service_exception.UpdateAnswerException(
                "service failed to update answer"
            ) from e

    async def delete(self, answer: proto.DeleteAnswer) -> domain.Answer:
        try:
            log.debug(f"deleting answer {answer.id}")
            return await self._form_field_repo.delete_answer(answer)
        except Exception as e:
            log.error("failed to delete answer with error: {}", e)
            raise service_exception.DeleteAnswerException(
                "service failed to delete answer"
            ) from e

    async def read_many(self, answers: list[proto.ReadAnswer]) -> list[domain.Answer]:
        try:
            log.debug(f"reading answers {[str(answer.id) for  answer in answers]}")
            documents = await self._form_field_repo.read_many_answers(answers)
            results = []
            for request, response in zip(answers, documents, strict=True):
                if response is None:
                    log.error(f"failed to read answer {request.id}")
                    raise service_exception.ReadAnswerException(
                        f"failed to read answer {request.id}"
                    )

                results.append(response)
            log.info(f"read answers {[str(answer.id) for  answer in answers]}")
            return results
        except service_exception.ServiceException as e:
            log.error("failed to read answers with error: {}", e)
            raise e
        except ValueError as e:  # raised by zip
            log.error("failed to read answers with error: {}", e)
            raise service_exception.ReadAnswerException("failed to read answers") from e
        except Exception as e:
            log.error("failed to read answers with error: {}", e)
            raise service_exception.ReadAnswerException("failed to read answers") from e

    async def read_all(self) -> list[domain.Answer]:
        try:
            log.debug("reading all answers")
            return await self._form_field_repo.read_all_answers()
        except Exception as e:
            log.error("failed to read all answers with error: {}", e)
            raise service_exception.ReadAnswerException(
                "service failed to read all answers"
            ) from e

    def __check_choice_answer(
        self,
        answer: proto.CreateChoiceAnswer | proto.UpdateChoiceAnswer,
        question: domain.FormField,
    ) -> None:
        log.debug("checking choice answer is to choice question")
        if not isinstance(question, domain.ChoiceFormField):
            raise service_exception.CreateAnswerException(
                "can not create choice answer for non choice question"
            )

        if answer.option_indexes is not None:
            log.debug("checking choice answer option indexes")

            log.debug(
                "checking choice answer selected options is not empty for required question"
            )
            if question.required and len(answer.option_indexes) == 0:
                log.error("can not create empty choice answer for required question")
                raise service_exception.CreateAnswerException(
                    "can not create empty choice answer for required question"
                )

            log.debug(
                "checking choice answer selected options is not multiple for single choice question"
            )
            if not question.multiple and len(answer.option_indexes) > 1:
                log.error(
                    "can not create multiple choice answer for single choice question"
                )
                raise service_exception.CreateAnswerException(
                    "can not create multiple choice answer for single choice question"
                )

    def __check_text_answer(
        self,
        answer: proto.CreateTextAnswer | proto.UpdateTextAnswer,
        question: domain.FormField,
    ) -> None:
        log.debug("checking text answer is to text question")
        if not isinstance(question, domain.TextFormField):
            log.error("can not create text for non text question")
            raise service_exception.CreateAnswerException(
                "can not create text answer for non text question"
            )

        if answer.text is not None:
            log.debug("checking text answer text is not empty for required question")
            if question.required and len(answer.text) == 0:
                log.error("can not create empty text answer for required question")
                raise service_exception.CreateAnswerException(
                    "can not create empty text answer for required question"
                )
