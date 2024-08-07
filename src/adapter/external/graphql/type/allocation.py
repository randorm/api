import strawberry as sb

import src.domain.model.allocation as domain
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool import resolver
from src.adapter.external.graphql.tool.permission import DefaultPermissions
from src.domain.model.allocation import (
    AllocationState,
    BaseAllocation,
    ClosedAllocation,
    CreatedAllocation,
    CreatingAllocation,
    FailedAllocation,
    OpenAllocation,
    RoomedAllocation,
    RoomingAllocation,
)

AllocationStateType = sb.enum(AllocationState)


@sb.experimental.pydantic.interface(model=BaseAllocation)
class BaseAllocationType:
    id: scalar.ObjectID = sb.field(name="id")
    created_at: sb.auto
    updated_at: sb.auto
    deleted_at: sb.auto

    name: sb.auto
    due: sb.auto
    state: AllocationStateType  # type: ignore

    form_fields_ids: list[scalar.ObjectID]
    form_fields: list[resolver.LazyFormFieldType] = sb.field(  # type: ignore
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_form_fields,
    )

    creator_id: scalar.ObjectID
    creator: resolver.LazyUserType = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_creator,
    )

    editors_ids: list[scalar.ObjectID]
    editors: list[resolver.LazyUserType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_editors,
    )


@sb.experimental.pydantic.type(model=CreatingAllocation)
class CreatingAllocationType(BaseAllocationType):
    state: AllocationStateType = sb.field(default=AllocationStateType.CREATING)  # type: ignore


@sb.experimental.pydantic.type(model=CreatedAllocation)
class CreatedAllocationType(BaseAllocationType):
    state: AllocationStateType = sb.field(default=AllocationStateType.CREATED)  # type: ignore

    participants_ids: list[scalar.ObjectID]
    participants: list[resolver.LazyUserType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_participants,
    )


@sb.experimental.pydantic.type(model=OpenAllocation)
class OpenAllocationType(BaseAllocationType):
    state: AllocationStateType = sb.field(default=AllocationStateType.OPEN)  # type: ignore

    participants_ids: list[scalar.ObjectID]
    participants: list[resolver.LazyUserType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_participants,
    )


@sb.experimental.pydantic.type(model=RoomingAllocation)
class RoomingAllocationType(BaseAllocationType):
    state: AllocationStateType = sb.field(default=AllocationStateType.ROOMING)  # type: ignore

    participants_ids: list[scalar.ObjectID]
    participants: list[resolver.LazyUserType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_participants,
    )


@sb.experimental.pydantic.type(model=RoomedAllocation)
class RoomedAllocationType(BaseAllocationType):
    state: AllocationStateType = sb.field(default=AllocationStateType.ROOMED)  # type: ignore

    participants_ids: list[scalar.ObjectID]
    participants: list[resolver.LazyUserType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_participants,
    )


@sb.experimental.pydantic.type(model=ClosedAllocation)
class ClosedAllocationType(BaseAllocationType):
    state: AllocationStateType = sb.field(default=AllocationStateType.CLOSED)  # type: ignore

    participants_ids: list[scalar.ObjectID]
    participants: list[resolver.LazyUserType] = sb.field(
        permission_classes=[DefaultPermissions],
        resolver=resolver.load_participants,
    )


@sb.experimental.pydantic.type(model=FailedAllocation)
class FailedAllocationType(BaseAllocationType):
    state: AllocationStateType = sb.field(default=AllocationStateType.FAILED)  # type: ignore


AllocationType = sb.union(
    "AllocationType",
    types=(
        CreatingAllocationType,
        CreatedAllocationType,
        OpenAllocationType,
        RoomingAllocationType,
        RoomedAllocationType,
        ClosedAllocationType,
        FailedAllocationType,
    ),
)


def domain_to_allocation(data: domain.Allocation) -> AllocationType:  # type: ignore
    match data:
        case domain.CreatingAllocation():
            return CreatingAllocationType.from_pydantic(data)
        case domain.CreatedAllocation():
            return CreatedAllocationType.from_pydantic(data)
        case domain.OpenAllocation():
            return OpenAllocationType.from_pydantic(data)
        case domain.RoomingAllocation():
            return RoomingAllocationType.from_pydantic(data)
        case domain.RoomedAllocation():
            return RoomedAllocationType.from_pydantic(data)
        case domain.ClosedAllocation():
            return ClosedAllocationType.from_pydantic(data)
        case domain.FailedAllocation():
            return FailedAllocationType.from_pydantic(data)
