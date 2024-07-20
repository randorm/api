from dataclasses import dataclass

import strawberry as sb
from strawberry.dataloader import DataLoader

from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.type.allocation import AllocationType
from src.adapter.external.graphql.type.form_field import AnswerType, FormFieldType
from src.adapter.external.graphql.type.participant import ParticipantType
from src.adapter.external.graphql.type.preference import PreferenceType
from src.adapter.external.graphql.type.room import RoomType
from src.adapter.external.graphql.type.user import UserType
from src.service import answer
from src.service.allocation import AllocationService
from src.service.form_field import FormFieldService
from src.service.participant import ParticipantService
from src.service.preference import PreferenceService
from src.service.room import RoomService
from src.service.user import UserService


@dataclass
class DataContext[LoaderType, ServiceType]:
    loader: DataLoader[scalar.ObjectID, LoaderType]
    service: ServiceType


@dataclass
class Context:
    answer: DataContext[AnswerType, answer.AnswerService]  # type: ignore
    allocation: DataContext[AllocationType, AllocationService]  # type: ignore
    form_field: DataContext[FormFieldType, FormFieldService]  # type: ignore
    participant: DataContext[ParticipantType, ParticipantService]  # type: ignore
    preference: DataContext[PreferenceType, PreferenceService]
    room: DataContext[RoomType, RoomService]
    user: DataContext[UserType, UserService]


type Info[T] = sb.Info[Context, T]
