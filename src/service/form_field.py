import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database as proto
from src.service import common
from src.service.base import BaseService


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
            if not await common.check_creator_exist(form_field, self._user_repo):
                raise service_exception.CreateFormFieldException(
                    "creator does not exist"
                )

            if not await common.check_editors_exist(form_field, self._user_repo):
                raise service_exception.CreateFormFieldException(
                    "one or more editors do not exist"
                )

            return await self._form_field_repo.create_form_field(form_field)
        except service_exception.ServiceException as e:
            raise e
        except Exception as e:
            raise service_exception.CreateFormFieldException(
                "service failed to create form field"
            ) from e

    async def read(self, form_field: proto.ReadFormField) -> domain.FormField:
        try:
            return await self._form_field_repo.read_form_field(form_field)
        except Exception as e:
            raise service_exception.ReadFormFieldException(
                "service failed to read form field"
            ) from e

    async def update(self, form_field: proto.UpdateFormField) -> domain.FormField:
        try:
            try:
                current = await self._form_field_repo.read_form_field(
                    proto.ReadFormField(_id=form_field.id)
                )
            except Exception as e:
                raise service_exception.UpdateFormFieldException(
                    "form field does not exist"
                ) from e

            if current.frozen:
                raise service_exception.UpdateFormFieldException(
                    "can not update frozen form field"
                )

            if current.creator_id is not None:
                raise service_exception.UpdateFormFieldException(
                    "creator can not be changed"
                )

            return await self._form_field_repo.update_form_field(form_field)
        except service_exception.ServiceException as e:
            raise e
        except Exception as e:
            raise service_exception.UpdateFormFieldException(
                "service failed to update form field"
            ) from e

    async def delete(self, form_field: proto.DeleteFormField) -> domain.FormField:
        try:
            return await self._form_field_repo.delete_form_field(form_field)
        except Exception as e:
            raise service_exception.DeleteFormFieldException(
                "service failed to delete form field"
            ) from e

    async def read_many(
        self, form_fields: list[proto.ReadFormField]
    ) -> list[domain.FormField]:
        try:
            documents = await self._form_field_repo.read_many_form_fields(form_fields)
            results = []
            for request, response in zip(form_fields, documents, strict=True):
                if response is None:
                    raise service_exception.ReadFormFieldException(
                        f"failed to read form field {request.id}"
                    )

                results.append(response)

            return results
        except service_exception.ServiceException as e:
            raise e
        except ValueError as e:  # raised by zip
            raise service_exception.ReadFormFieldException(
                "failed to read form fields"
            ) from e
        except Exception as e:
            raise service_exception.ReadFormFieldException(
                "failed to read form fields"
            ) from e
