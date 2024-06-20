from enum import StrEnum
from typing import Annotated

import strawberry as sb

from src.domain.model.format_entity import (
    BaseFormatEntity,
    BoldEntity,
    CodeEntity,
    FormatOption,
    ItalicEntity,
    LinkEntity,
    MonospaceEntity,
    SpoilerEntity,
    StrikethroughEntity,
    UnderlineEntity,
)


@sb.enum
class FormatOptionType(StrEnum):
    SPOILER = FormatOption.SPOILER.value
    BOLD = FormatOption.BOLD.value
    ITALIC = FormatOption.ITALIC.value
    MONOSPACE = FormatOption.MONOSPACE.value
    LINK = FormatOption.LINK.value
    STRIKETHROUGH = FormatOption.STRIKETHROUGH.value
    UNDERLINE = FormatOption.UNDERLINE.value
    CODE = FormatOption.CODE.value


@sb.experimental.pydantic.interface(model=BaseFormatEntity)
class BaseFormatEntityType:
    option: FormatOptionType
    offset: sb.auto
    length: sb.auto


@sb.experimental.pydantic.type(model=SpoilerEntity)
class SpoilerEntityType(BaseFormatEntityType):
    option: FormatOptionType = FormatOptionType.SPOILER


@sb.experimental.pydantic.type(model=BoldEntity)
class BoldEntityType(BaseFormatEntityType):
    option: FormatOptionType = FormatOptionType.BOLD


@sb.experimental.pydantic.type(model=ItalicEntity)
class ItalicEntityType(BaseFormatEntityType):
    option: FormatOptionType = FormatOptionType.ITALIC


@sb.experimental.pydantic.type(model=MonospaceEntity)
class MonospaceEntityType(BaseFormatEntityType):
    option: FormatOptionType = FormatOptionType.MONOSPACE


@sb.experimental.pydantic.type(model=LinkEntity)
class LinkEntityType(BaseFormatEntityType):
    option: FormatOptionType = FormatOptionType.LINK
    url: sb.auto


@sb.experimental.pydantic.type(model=StrikethroughEntity)
class StrikethroughEntityType(BaseFormatEntityType):
    option: FormatOptionType = FormatOptionType.STRIKETHROUGH


@sb.experimental.pydantic.type(model=UnderlineEntity)
class UnderlineEntityType(BaseFormatEntityType):
    option: FormatOptionType = FormatOptionType.UNDERLINE


@sb.experimental.pydantic.type(model=CodeEntity)
class CodeEntityType(BaseFormatEntityType):
    option: FormatOptionType = FormatOptionType.CODE
    language: sb.auto


type FormatEntityType = Annotated[
    SpoilerEntityType
    | BoldEntityType
    | ItalicEntityType
    | MonospaceEntityType
    | LinkEntityType
    | StrikethroughEntityType
    | UnderlineEntityType
    | CodeEntityType,
    sb.union("FormatEntityType"),
]
