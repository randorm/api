import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.service import common


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
            if not await common.check_form_field_exist(answer, self._form_field_repo):
                raise service_exception.CreateAnswerException(
                    "form field does not exist"
                )

            if not await common.check_respondent_exist(answer, self._participant_repo):
                raise service_exception.CreateAnswerException(
                    "participant does not exist"
                )

            question = await self._form_field_repo.read_form_field(
                proto.ReadFormField(_id=answer.form_field_id)
            )

            if isinstance(answer, proto.CreateChoiceAnswer):
                self.__check_choice_answer(answer, question)

            if isinstance(answer, proto.CreateTextAnswer):
                self.__check_text_answer(answer, question)

            return await self._form_field_repo.create_answer(answer)

        except service_exception.ServiceException as e:
            raise e
        except Exception as e:
            raise service_exception.CreateAnswerException(
                "service failed to create answer"
            ) from e

    async def read(self, answer: proto.ReadAnswer) -> domain.Answer:
        try:
            return await self._form_field_repo.read_answer(answer)
        except Exception as e:
            raise service_exception.ReadAnswerException(
                "service failed to read answer"
            ) from e

    async def update(self, answer: proto.UpdateAnswer) -> domain.Answer:
        try:
            try:
                current = await self._form_field_repo.read_answer(
                    proto.ReadAnswer(_id=answer.id)
                )
            except Exception as e:
                raise service_exception.UpdateAnswerException(
                    "answer does not exist"
                ) from e

            if answer.kind != current.kind:
                raise service_exception.UpdateAnswerException(
                    "can not change answer type"
                )

            if answer.respondent_id is not None:
                raise service_exception.UpdateAnswerException(
                    "can not change respondent"
                )

            if answer.form_field_id is not None:
                raise service_exception.UpdateAnswerException(
                    "can not change form field"
                )

            question = await self._form_field_repo.read_form_field(
                proto.ReadFormField(_id=current.form_field_id)
            )

            if isinstance(answer, proto.UpdateChoiceAnswer):
                self.__check_choice_answer(answer, question)

            if isinstance(answer, proto.UpdateTextAnswer):
                self.__check_text_answer(answer, question)

            return await self._form_field_repo.update_answer(answer)
        except service_exception.ServiceException as e:
            raise e
        except Exception as e:
            raise service_exception.UpdateAnswerException(
                "service failed to update answer"
            ) from e

    async def delete(self, answer: proto.DeleteAnswer) -> domain.Answer:
        try:
            return await self._form_field_repo.delete_answer(answer)
        except Exception as e:
            raise service_exception.DeleteAnswerException(
                "service failed to delete answer"
            ) from e

    async def read_many(self, answers: list[proto.ReadAnswer]) -> list[domain.Answer]:
        try:
            documents = await self._form_field_repo.read_many_answers(answers)
            results = []
            for request, response in zip(answers, documents, strict=True):
                if response is None:
                    raise service_exception.ReadAnswerException(
                        f"failed to read answer {request.id}"
                    )

                results.append(response)

            return results
        except service_exception.ServiceException as e:
            raise e
        except ValueError as e:  # raised by zip
            raise service_exception.ReadAnswerException("failed to read answers") from e
        except Exception as e:
            raise service_exception.ReadAnswerException("failed to read answers") from e

    def __check_choice_answer(
        self,
        answer: proto.CreateChoiceAnswer | proto.UpdateChoiceAnswer,
        question: domain.FormField,
    ) -> None:
        if not isinstance(question, domain.ChoiceFormField):
            raise service_exception.CreateAnswerException(
                "can not create choice answer for non choice question"
            )

        if answer.option_indexes is not None:
            if question.required and len(answer.option_indexes) == 0:
                raise service_exception.CreateAnswerException(
                    "can not create empty choice answer for required question"
                )

            if not question.multiple and len(answer.option_indexes) > 1:
                raise service_exception.CreateAnswerException(
                    "can not create multiple choice answer for single choice question"
                )

    def __check_text_answer(
        self,
        answer: proto.CreateTextAnswer | proto.UpdateTextAnswer,
        question: domain.FormField,
    ) -> None:
        if not isinstance(question, domain.TextFormField):
            raise service_exception.CreateAnswerException(
                "can not create text answer for non text question"
            )

        if answer.text is not None:
            if question.required and len(answer.text) == 0:
                raise service_exception.CreateAnswerException(
                    "can not create empty text answer for required question"
                )
