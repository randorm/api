import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.service import common
from src.service.base import BaseService
from src.utils.logger.logger import Logger

log = Logger("form-field-service")


class FormFieldService(BaseService):
    def __init__(
        self,
        allocation_repo: proto.AllocationDatabaseProtocol,
        form_field_repo: proto.FormFieldDatabaseProtocol,
        user_repo: proto.UserDatabaseProtocol,
    ):
        self._allocation_repo = allocation_repo
        self._form_field_repo = form_field_repo
        self._user_repo = user_repo

    async def create(self, form_field: proto.CreateFormField) -> domain.FormField:
        try:
            log.debug("creating new form field")

            log.debug("checking form field creator existence")
            if not await common.check_creator_exist(form_field, self._user_repo):
                log.error("creator does not exist")
                raise service_exception.CreateFormFieldException(
                    "creator does not exist"
                )

            log.debug("checking form field editors existence")
            if not await common.check_editors_exist(form_field, self._user_repo):
                log.error("one or more editors do not exist")
                raise service_exception.CreateFormFieldException(
                    "one or more editors do not exist"
                )

            log.debug("creating new form field")
            return await self._form_field_repo.create_form_field(form_field)
        except service_exception.ServiceException as e:
            log.error("failed to create form field with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to create form field with error: {}", e)
            raise service_exception.CreateFormFieldException(
                "service failed to create form field"
            ) from e

    async def read(self, form_field: proto.ReadFormField) -> domain.FormField:
        try:
            log.debug(f"reading form field {form_field.id}")
            return await self._form_field_repo.read_form_field(form_field)
        except Exception as e:
            log.error("failed to read form field with error: {}", e)
            raise service_exception.ReadFormFieldException(
                "service failed to read form field"
            ) from e

    async def update(self, form_field: proto.UpdateFormField) -> domain.FormField:
        try:
            log.debug(f"updating form field {form_field.id}")
            try:
                log.debug(f"reading form field {form_field.id}")
                current = await self._form_field_repo.read_form_field(
                    proto.ReadFormField(_id=form_field.id)
                )
            except Exception as e:
                log.error("failed to read form field with error: {}", e)
                raise service_exception.UpdateFormFieldException(
                    "form field does not exist"
                ) from e

            log.debug("checking form field frozen")
            if current.frozen:
                log.error("can not update frozen form field")
                raise service_exception.UpdateFormFieldException(
                    "can not update frozen form field"
                )

            log.debug("checking form field creator non-updateability")
            if current.creator_id is not None:
                log.error("creator can not be changed")
                raise service_exception.UpdateFormFieldException(
                    "creator can not be changed"
                )

            return await self._form_field_repo.update_form_field(form_field)
        except service_exception.ServiceException as e:
            log.error("failed to update form field with error: {}", e)
            raise e
        except Exception as e:
            log.error("failed to update form field with error: {}", e)
            raise service_exception.UpdateFormFieldException(
                "service failed to update form field"
            ) from e

    async def delete(self, form_field: proto.DeleteFormField) -> domain.FormField:
        try:
            log.debug(f"deleting form field {form_field.id}")
            return await self._form_field_repo.delete_form_field(form_field)
        except Exception as e:
            log.error("failed to delete form field with error: {}", e)
            raise service_exception.DeleteFormFieldException(
                "service failed to delete form field"
            ) from e

    async def read_many(
        self, form_fields: list[proto.ReadFormField]
    ) -> list[domain.FormField]:
        try:
            log.debug(
                f"reading form fields {[str(form_field.id) for  form_field in form_fields]}"
            )
            documents = await self._form_field_repo.read_many_form_fields(form_fields)
            results = []
            for request, response in zip(form_fields, documents, strict=True):
                if response is None:
                    log.error(f"failed to read form field {request.id}")
                    raise service_exception.ReadFormFieldException(
                        f"failed to read form field {request.id}"
                    )

                results.append(response)
            log.info(
                f"read form fields {[str(form_field.id) for  form_field in form_fields]}"
            )
            return results
        except service_exception.ServiceException as e:
            log.error("failed to read form fields with error: {}", e)
            raise e
        except ValueError as e:  # raised by zip
            log.error("failed to read form fields with error: {}", e)
            raise service_exception.ReadFormFieldException(
                "failed to read form fields"
            ) from e
        except Exception as e:
            log.error("failed to read form fields with error: {}", e)
            raise service_exception.ReadFormFieldException(
                "failed to read form fields"
            ) from e
