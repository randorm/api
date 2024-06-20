from datetime import datetime

from pydantic import BaseModel, Field, SkipJsonSchema


class ExcludeFieldMixin(BaseModel):
    id: SkipJsonSchema[int | None] = Field(default=None, exclude=True)  # type: ignore
    created_at: SkipJsonSchema[datetime | None] = Field(default=None, exclude=True)  # type: ignore
    updated_at: SkipJsonSchema[datetime | None] = Field(default=None, exclude=True)  # type: ignore
    deleted_at: SkipJsonSchema[datetime | None] = Field(default=None, exclude=True)  # type: ignore
