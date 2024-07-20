from collections.abc import Sequence
from datetime import datetime
from typing import Any, Protocol

import src.domain.model as domain
from src.protocol.internal.database.form_field import (
    FormFieldDatabaseProtocol,
    ReadFormField,
)
from src.protocol.internal.database.participant import (
    ParticipantDatabaseProtocol,
    ReadParticipant,
)
from src.protocol.internal.database.user import ReadUser, UserDatabaseProtocol


def _any_none(data: list[Any | None]) -> bool:
    return any(item is None for item in data)


class WithDeleted(Protocol):
    deleted_at: datetime | None


def _any_deleted(data: Sequence[WithDeleted | None]) -> bool:
    return any(item.deleted_at is not None for item in data if item is not None)


class WithCreator(Protocol):
    creator_id: domain.ObjectID


async def check_creator_exist(obj: WithCreator, db: UserDatabaseProtocol) -> bool:
    try:
        data = await db.read_many_users([ReadUser(_id=obj.creator_id)])

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


async def check_editors_exist(obj: WithEditors, db: UserDatabaseProtocol) -> bool:
    try:
        data = await db.read_many_users(
            [ReadUser(_id=item) for item in obj.editors_ids]
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
    obj: WithFormFields, db: FormFieldDatabaseProtocol
) -> bool:
    try:
        data = await db.read_many_form_fields(
            [ReadFormField(_id=item) for item in obj.form_fields_ids]
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
    obj: WithParticipants, db: ParticipantDatabaseProtocol
) -> bool:
    try:
        data = await db.read_many_participants(
            [ReadParticipant(_id=item) for item in obj.participants_ids]
        )

        if any(item is None for item in data):
            return False

        # if _any_deleted(data):
        #     return False

    except Exception:
        return False
    else:
        return True
