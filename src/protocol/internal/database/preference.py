from abc import ABC, abstractmethod
from typing import Literal

from pydantic import BaseModel, Field

import src.domain.model as domain
from src.protocol.internal.database.mixin import ExcludeFieldMixin


class CreatePreference(ExcludeFieldMixin, domain.Preference): ...


class ReadPreference(BaseModel):
    id: domain.ObjectID = Field(alias="_id")


class UpdatePreference(ExcludeFieldMixin, domain.Preference):
    id: domain.ObjectID = Field(alias="_id")  # type: ignore
    # optional fields
    kind: domain.PreferenceKind | None = Field(default=None)
    status: domain.PreferenceStatus | None = Field(default=None)
    # exclude
    user_id: Literal[None] = None
    target_id: Literal[None] = None


class DeletePreference(BaseModel):
    id: domain.ObjectID = Field(alias="_id")


class PreferenceDatabaseProtocol(ABC):
    @abstractmethod
    async def create_preference(
        self, preference: CreatePreference
    ) -> domain.Preference: ...

    @abstractmethod
    async def read_preference(
        self, preference: ReadPreference
    ) -> domain.Preference: ...

    @abstractmethod
    async def update_preference(
        self, preference: UpdatePreference
    ) -> domain.Preference: ...

    @abstractmethod
    async def delete_preference(
        self, preference: DeletePreference
    ) -> domain.Preference: ...
