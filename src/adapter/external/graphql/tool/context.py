from typing import Any

import pydantic
from strawberry.dataloader import DataLoader

from src.adapter.external.graphql import scalar


class Context(pydantic.BaseModel):
    loaders: DataLoader[scalar.ObjectID, Any]

    model_config = pydantic.ConfigDict(arbitrary_types_allowed=True)
