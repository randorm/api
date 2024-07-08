from src.domain.exception.base import DomainException


class DatabaseException(DomainException): ...


class AllocationException(DatabaseException): ...


class ParticipantException(DatabaseException): ...


class FormFieldException(DatabaseException): ...


class AnswerException(DatabaseException): ...


class UserException(DatabaseException): ...


class RoomException(DatabaseException): ...


class ReflectAlloctionException(AllocationException): ...


class ReflectFormFieldException(FormFieldException): ...


class ReflectAnswerException(AnswerException): ...


class ReflectUserException(UserException): ...


class ReflectRoomException(RoomException): ...


class ReflectParticipantException(ParticipantException): ...


class CreateAllocationException(AllocationException): ...


class ReadAllocationException(AllocationException): ...


class UpdateAllocationException(AllocationException): ...


class DeleteAllocationException(AllocationException): ...


class CreateFormFieldException(FormFieldException): ...


class ReadFormFieldException(FormFieldException): ...


class UpdateFormFieldException(FormFieldException): ...


class DeleteFormFieldException(FormFieldException): ...


class CreateAnswerException(AnswerException): ...


class ReadAnswerException(AnswerException): ...


class UpdateAnswerException(AnswerException): ...


class DeleteAnswerException(AnswerException): ...


class CreateUserException(UserException): ...


class FindUsersException(UserException): ...


class ReadUserException(UserException): ...


class UpdateUserException(UserException): ...


class DeleteUserException(UserException): ...


class CreateRoomException(RoomException): ...


class ReadRoomException(RoomException): ...


class UpdateRoomException(RoomException): ...


class DeleteRoomException(RoomException): ...


class CreateParticipantException(ParticipantException): ...


class ReadParticipantException(ParticipantException): ...


class UpdateParticipantException(ParticipantException): ...


class DeleteParticipantException(ParticipantException): ...


class PreferenceException(DatabaseException): ...


class CreatePreferenceException(PreferenceException): ...


class ReadPreferenceException(PreferenceException): ...


class UpdatePreferenceException(PreferenceException): ...


class DeletePreferenceException(PreferenceException): ...


class ReflectPreferenceException(PreferenceException): ...
