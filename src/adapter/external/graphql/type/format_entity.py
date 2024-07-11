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
    option: FormatOptionType = sb.field(default=FormatOptionType.SPOILER)  # type: ignore


@sb.experimental.pydantic.type(model=BoldEntity)
class BoldEntityType(BaseFormatEntityType):
    option: FormatOptionType = sb.field(default=FormatOptionType.BOLD)  # type: ignore


@sb.experimental.pydantic.type(model=ItalicEntity)
class ItalicEntityType(BaseFormatEntityType):
    option: FormatOptionType = sb.field(default=FormatOptionType.ITALIC)  # type: ignore


@sb.experimental.pydantic.type(model=MonospaceEntity)
class MonospaceEntityType(BaseFormatEntityType):
    option: FormatOptionType = sb.field(default=FormatOptionType.MONOSPACE)  # type: ignore


@sb.experimental.pydantic.type(model=LinkEntity)
class LinkEntityType(BaseFormatEntityType):
    option: FormatOptionType = sb.field(default=FormatOptionType.LINK)  # type: ignore
    url: sb.auto


@sb.experimental.pydantic.type(model=StrikethroughEntity)
class StrikethroughEntityType(BaseFormatEntityType):
    option: FormatOptionType = sb.field(default=FormatOptionType.STRIKETHROUGH)  # type: ignore


@sb.experimental.pydantic.type(model=UnderlineEntity)
class UnderlineEntityType(BaseFormatEntityType):
    option: FormatOptionType = sb.field(default=FormatOptionType.UNDERLINE)  # type: ignore


@sb.experimental.pydantic.type(model=CodeEntity)
class CodeEntityType(BaseFormatEntityType):
    option: FormatOptionType = sb.field(default=FormatOptionType.CODE)  # type: ignore
    language: sb.auto


FormatEntityType = sb.union(
    "FormatEntityType",
    types=(
        SpoilerEntityType,
        BoldEntityType,
        ItalicEntityType,
        MonospaceEntityType,
        LinkEntityType,
        StrikethroughEntityType,
        UnderlineEntityType,
        CodeEntityType,
    ),
)
