"""
Database Protocols module.
All protocols related to CRUD operations with databases should be defined here.
"""

from src.protocol.internal.database import (
    allocation,
    form_field,
    mixin,
    participant,
    room,
    user,
)
from src.protocol.internal.database.allocation import (
    AllocationDatabaseProtocol,
    CreateAllocation,
    CreateClosedAllocation,
    CreateCreatedAllocation,
    CreateCreatingAllocation,
    CreateFailedAllocation,
    CreateOpenAllocation,
    CreateRoomedAllocation,
    CreateRoomingAllocation,
    DeleteAllocation,
    ReadAllocation,
    UpdateAllocation,
)
from src.protocol.internal.database.form_field import (
    CreateAnswer,
    CreateChoiceAnswer,
    CreateChoiceFormField,
    CreateFormField,
    CreateTextAnswer,
    CreateTextFormField,
    DeleteAnswer,
    DeleteFormField,
    FormFieldDatabaseProtocol,
    ReadAnswer,
    ReadFormField,
    UpdateAnswer,
    UpdateChoiceAnswer,
    UpdateChoiceFormField,
    UpdateChoiceOption,
    UpdateFormField,
    UpdateTextAnswer,
    UpdateTextFormField,
)
from src.protocol.internal.database.mixin import ExcludeFieldMixin
from src.protocol.internal.database.participant import (
    CreateActiveParticipant,
    CreateAllocatedParticipant,
    CreateCreatedParticipant,
    CreateCreatingParticipant,
    CreateParticipant,
    DeleteParticipant,
    ParticipantDatabaseProtocol,
    ReadParticipant,
    UpdateParticipant,
)
from src.protocol.internal.database.preference import (
    CreatePreference,
    DeletePreference,
    FindPreference,
    PreferenceDatabaseProtocol,
    ReadPreference,
    UpdatePreference,
)
from src.protocol.internal.database.room import (
    CreateRoom,
    DeleteRoom,
    ReadRoom,
    RoomDatabaseProtocol,
    UpdateRoom,
)
from src.protocol.internal.database.user import (
    CreateUser,
    DeleteUser,
    FindUsers,
    FindUsersByProfileUsername,
    FindUsersByTid,
    ReadUser,
    UpdateUser,
    UserDatabaseProtocol,
)
