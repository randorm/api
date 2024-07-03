from src.domain.exception.base import DomainException


class ServiceException(DomainException): ...


class CreateUserException(ServiceException): ...
