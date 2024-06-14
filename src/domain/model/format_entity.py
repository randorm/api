from enum import StrEnum

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
    option: FormatOption = FormatOption.SPOILER


class BoldEntity(BaseFormatEntity, frozen=True):
    option: FormatOption = FormatOption.BOLD


class ItalicEntity(BaseFormatEntity, frozen=True):
    option: FormatOption = FormatOption.ITALIC


class MonospaceEntity(BaseFormatEntity, frozen=True):
    option: FormatOption = FormatOption.MONOSPACE


class LinkEntity(BaseFormatEntity, frozen=True):
    option: FormatOption = FormatOption.LINK
    url: pydantic.HttpUrl


class StrikethroughEntity(BaseFormatEntity, frozen=True):
    option: FormatOption = FormatOption.STRIKETHROUGH


class UnderlineEntity(BaseFormatEntity, frozen=True):
    option: FormatOption = FormatOption.UNDERLINE


class CodeEntity(BaseFormatEntity, frozen=True):
    option: FormatOption = FormatOption.CODE
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
