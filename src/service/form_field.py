import src.domain.model as domain
import src.protocol.internal.database.form_field as proto
from src.service.base import BaseService


class FormFieldService(BaseService):
    def __init__(self, repo: proto.FormFieldDatabaseProtocol):
        self._repo = repo

    async def create(self, form_field: proto.CreateFormField) -> domain.FormField:
        raise NotImplementedError()

    async def read(self, form_field: proto.ReadFormField) -> domain.FormField:
        raise NotImplementedError()

    async def update(self, form_field: proto.UpdateFormField) -> domain.FormField:
        raise NotImplementedError()

    async def delete(self, form_field: proto.DeleteFormField) -> domain.FormField:
        raise NotImplementedError()
