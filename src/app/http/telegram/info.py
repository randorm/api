from dataclasses import dataclass

from src.service.allocation import AllocationService
from src.service.answer import AnswerService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService


@dataclass
class Services:
    allocation: AllocationService
    answer: AnswerService
    form_field: FormFieldService
    participant: ParticipantService
    preference: PreferenceService
    room: RoomService
    user: UserService


@dataclass
class TelegramInfo:
    srv: Services
