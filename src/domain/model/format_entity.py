from enum import StrEnum
from typing import Literal

import pydantic


class FormatOption(StrEnum):
    SPOILER = "spoiler"
    BOLD = "bold"
    ITALIC = "italic"
    MONOSPACE = "monospace"
    LINK = "link"
    STRIKETHROUGH = "strikethrough"
    UNDERLINE = "underline"
    CODE = "code"


class BaseFormatEntity(pydantic.BaseModel, frozen=True):
    option: FormatOption
    offset: int
    length: int


class SpoilerEntity(BaseFormatEntity, frozen=True):
    option: Literal[FormatOption.SPOILER] = FormatOption.SPOILER


class BoldEntity(BaseFormatEntity, frozen=True):
    option: Literal[FormatOption.BOLD] = FormatOption.BOLD


class ItalicEntity(BaseFormatEntity, frozen=True):
    option: Literal[FormatOption.ITALIC] = FormatOption.ITALIC


class MonospaceEntity(BaseFormatEntity, frozen=True):
    option: Literal[FormatOption.MONOSPACE] = FormatOption.MONOSPACE


class LinkEntity(BaseFormatEntity, frozen=True):
    option: Literal[FormatOption.LINK] = FormatOption.LINK
    url: pydantic.HttpUrl


class StrikethroughEntity(BaseFormatEntity, frozen=True):
    option: Literal[FormatOption.STRIKETHROUGH] = FormatOption.STRIKETHROUGH


class UnderlineEntity(BaseFormatEntity, frozen=True):
    option: Literal[FormatOption.UNDERLINE] = FormatOption.UNDERLINE


class CodeEntity(BaseFormatEntity, frozen=True):
    option: Literal[FormatOption.CODE] = FormatOption.CODE
    language: str


type FormatEntity = (
    SpoilerEntity
    | BoldEntity
    | ItalicEntity
    | MonospaceEntity
    | LinkEntity
    | StrikethroughEntity
    | UnderlineEntity
    | CodeEntity
)

FormatEntityResolver = pydantic.TypeAdapter(
    type=FormatEntity,
    config=pydantic.ConfigDict(extra="ignore", from_attributes=True),
)
