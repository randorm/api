from collections.abc import Sequence
from datetime import datetime
from typing import Any, Protocol

import src.domain.model as domain
import src.protocol.internal.database as proto


def _any_none(data: list[Any | None]) -> bool:
    return any(item is None for item in data)


class WithDeleted(Protocol):
    deleted_at: datetime | None


def _any_deleted(data: Sequence[WithDeleted | None]) -> bool:
    return any(item.deleted_at is not None for item in data if item is not None)


class WithCreator(Protocol):
    creator_id: domain.ObjectID


async def check_creator_exist(obj: WithCreator, db: proto.UserDatabaseProtocol) -> bool:
    try:
        data = await db.read_many_users([proto.ReadUser(_id=obj.creator_id)])

        if _any_none(data):
            return False

        if _any_deleted(data):
            return False

    except Exception:
        return False
    else:
        return True


class WithEditors(Protocol):
    editors_ids: set[domain.ObjectID]


async def check_editors_exist(obj: WithEditors, db: proto.UserDatabaseProtocol) -> bool:
    try:
        data = await db.read_many_users(
            [proto.ReadUser(_id=item) for item in obj.editors_ids]
        )

        if _any_none(data):
            return False

        # allow deleted users
        # if _any_deleted(data):
        #     return False

        if any(item.deleted_at is not None for item in data if item is not None):
            return False

    except Exception:
        return False
    else:
        return True


class WithFormFields(Protocol):
    form_fields_ids: set[domain.ObjectID]


async def check_form_fields_exist(
    obj: WithFormFields, db: proto.FormFieldDatabaseProtocol
) -> bool:
    try:
        data = await db.read_many_form_fields(
            [proto.ReadFormField(_id=item) for item in obj.form_fields_ids]
        )

        if _any_none(data):
            return False

        if _any_deleted(data):
            return False

    except Exception:
        return False
    else:
        return True


class WithParticipants(Protocol):
    participants_ids: set[domain.ObjectID]


async def check_participants_exist(
    obj: WithParticipants, db: proto.ParticipantDatabaseProtocol
) -> bool:
    try:
        data = await db.read_many_participants(
            [proto.ReadParticipant(_id=item) for item in obj.participants_ids]
        )

        if any(item is None for item in data):
            return False

        # if _any_deleted(data):
        #     return False

    except Exception:
        return False
    else:
        return True


class WithAllocation(Protocol):
    allocation_id: domain.ObjectID


async def check_allocation_exist(
    obj: WithAllocation, db: proto.AllocationDatabaseProtocol
) -> bool:
    try:
        data = await db.read_many_allocations(
            [proto.ReadAllocation(_id=obj.allocation_id)]
        )

        if _any_none(data):
            return False

        if _any_deleted(data):
            return False

    except Exception:
        return False
    else:
        return True


class WithUser(Protocol):
    user_id: domain.ObjectID


async def check_user_exist(obj: WithUser, db: proto.UserDatabaseProtocol) -> bool:
    try:
        data = await db.read_many_users([proto.ReadUser(_id=obj.user_id)])

        if _any_none(data):
            return False

        if _any_deleted(data):
            return False
    except Exception:
        return False
    else:
        return True


class WithRoom(Protocol):
    room_id: domain.ObjectID


async def check_room_exist(obj: WithRoom, db: proto.RoomDatabaseProtocol) -> bool:
    try:
        data = await db.read_many_rooms([proto.ReadRoom(_id=obj.room_id)])

        if _any_none(data):
            return False

        if _any_deleted(data):
            return False

    except Exception:
        return False
    else:
        return True


class WithTarget(Protocol):
    target_id: domain.ObjectID


async def check_target_exist(obj: WithTarget, db: proto.UserDatabaseProtocol) -> bool:
    try:
        data = await db.read_many_users([proto.ReadUser(_id=obj.target_id)])

        if _any_none(data):
            return False

        if _any_deleted(data):
            return False

    except Exception:
        return False
    else:
        return True
