import src.domain.exception.service as service_exception
import src.domain.model as domain
import src.protocol.internal.database.form_field as proto
from src.service.base import BaseService

# todo: define all business logic


class FormFieldService(BaseService):
    def __init__(self, repo: proto.FormFieldDatabaseProtocol):
        self._repo = repo

    async def create(self, form_field: proto.CreateFormField) -> domain.FormField:
        try:
            return await self._repo.create_form_field(form_field)
        except Exception as e:
            raise service_exception.CreateFormFieldException(
                "service failed to create form field"
            ) from e

    async def read(self, form_field: proto.ReadFormField) -> domain.FormField:
        try:
            return await self._repo.read_form_field(form_field)
        except Exception as e:
            raise service_exception.ReadFormFieldException(
                "service failed to read form field"
            ) from e

    async def update(self, form_field: proto.UpdateFormField) -> domain.FormField:
        try:
            return await self._repo.update_form_field(form_field)
        except Exception as e:
            raise service_exception.UpdateFormFieldException(
                "service failed to update form field"
            ) from e

    async def delete(self, form_field: proto.DeleteFormField) -> domain.FormField:
        try:
            return await self._repo.delete_form_field(form_field)
        except Exception as e:
            raise service_exception.DeleteFormFieldException(
                "service failed to delete form field"
            ) from e
