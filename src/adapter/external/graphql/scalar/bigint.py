from typing import Union

import strawberry

BigInt = strawberry.scalar(
    Union[int, str],  # type: ignore # noqa: UP007
    serialize=lambda v: int(v),
    parse_value=lambda v: str(v),
    description="BigInt field",
)
