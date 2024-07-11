from __future__ import annotations

from datetime import datetime

import strawberry as sb

import src.adapter.external.graphql.type.allocation as graphql
import src.protocol.internal.database.allocation as proto
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info
from src.adapter.external.graphql.tool.permission import DefaultPermissions


@sb.type
class AllocationQuery:
    @sb.field(permission_classes=[DefaultPermissions])
    async def allocation(
        root: AllocationQuery, info: Info[AllocationQuery], id: scalar.ObjectID
    ) -> graphql.AllocationType:  # type: ignore
        return await info.context.allocation.loader.load(id)

    @sb.mutation
    async def create_allocation(
        root: AllocationQuery,
        info: Info[AllocationQuery],
        name: str,
        state: graphql.AllocationStateType,  # type: ignore
        creator_id: scalar.ObjectID,
        form_fields_ids: list[scalar.ObjectID] | None = None,
        due: datetime | None = None,
        editors_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.AllocationType:  # type: ignore
        request = proto.CreateAllocationResolver.validate_python(
            {
                "name": name,
                "due": due,
                "state": state,
                "form_fields_ids": set(form_fields_ids) if form_fields_ids else set(),
                "creator_id": creator_id,
                "editors_ids": set(editors_ids) if editors_ids else set(),
            }
        )

        data = await info.context.allocation.service.create(request)
        return graphql.domain_to_allocation(data)

    @sb.mutation
    async def update_allocation(
        root: AllocationQuery,
        info: Info[AllocationQuery],
        id: scalar.ObjectID,
        name: str | None = None,
        due: datetime | None = None,
        state: graphql.AllocationStateType | None = None,  # type: ignore
        form_fields_ids: list[scalar.ObjectID] | None = None,
        creator_id: scalar.ObjectID | None = None,
        editors_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.AllocationType:  # type: ignore
        request = proto.UpdateAllocation.model_validate(
            {
                "_id": id,
                "name": name,
                "due": due,
                "state": state,
                "form_fields_ids": form_fields_ids,
                "creator_id": creator_id,
                "editors_ids": editors_ids,
            }
        )
        data = await info.context.allocation.service.update(request)
        info.context.allocation.loader.clear(id)
        return graphql.domain_to_allocation(data)

    @sb.mutation
    async def delete_allocation(
        root: AllocationQuery, info: Info[AllocationQuery], id: scalar.ObjectID
    ) -> graphql.AllocationType:  # type: ignore
        data = await info.context.allocation.service.delete(
            proto.DeleteAllocation(_id=id)
        )
        info.context.allocation.loader.clear(id)
        return graphql.domain_to_allocation(data)
