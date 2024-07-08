from typing import Annotated, Literal

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

FormatOptionType = sb.enum(FormatOption)


@sb.experimental.pydantic.interface(model=BaseFormatEntity)
class BaseFormatEntityType:
    option: FormatOptionType  # type: ignore
    offset: sb.auto
    length: sb.auto


@sb.experimental.pydantic.type(model=SpoilerEntity)
class SpoilerEntityType(BaseFormatEntityType):
    option: Literal[FormatOptionType.SPOILER] = FormatOptionType.SPOILER


@sb.experimental.pydantic.type(model=BoldEntity)
class BoldEntityType(BaseFormatEntityType):
    option: Literal[FormatOptionType.BOLD] = FormatOptionType.BOLD


@sb.experimental.pydantic.type(model=ItalicEntity)
class ItalicEntityType(BaseFormatEntityType):
    option: Literal[FormatOptionType.ITALIC] = FormatOptionType.ITALIC


@sb.experimental.pydantic.type(model=MonospaceEntity)
class MonospaceEntityType(BaseFormatEntityType):
    option: Literal[FormatOptionType.MONOSPACE] = FormatOptionType.MONOSPACE


@sb.experimental.pydantic.type(model=LinkEntity)
class LinkEntityType(BaseFormatEntityType):
    option: Literal[FormatOptionType.LINK] = FormatOptionType.LINK
    url: sb.auto


@sb.experimental.pydantic.type(model=StrikethroughEntity)
class StrikethroughEntityType(BaseFormatEntityType):
    option: Literal[FormatOptionType.STRIKETHROUGH] = FormatOptionType.STRIKETHROUGH


@sb.experimental.pydantic.type(model=UnderlineEntity)
class UnderlineEntityType(BaseFormatEntityType):
    option: Literal[FormatOptionType.UNDERLINE] = FormatOptionType.UNDERLINE


@sb.experimental.pydantic.type(model=CodeEntity)
class CodeEntityType(BaseFormatEntityType):
    option: Literal[FormatOptionType.CODE] = FormatOptionType.CODE
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
