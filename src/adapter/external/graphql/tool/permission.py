from typing import TYPE_CHECKING, Annotated, Any

import strawberry as sb

from src.utils.logger.logger import Logger

if TYPE_CHECKING:
    from src.adapter.external.graphql.tool.context import Info

LazyInfo = Annotated[
    "Info",  # type: ignore
    sb.lazy(module_path="src.adapter.external.graphql.tool.context"),
]

log = Logger("graphql-permission")


class AuthenticatedPermission(sb.BasePermission):
    """Denies access to unauthenticated users"""

    message = "User is not authenticated"
    error_extensions = {"code": "UNAUTHORIZED"}

    def has_permission(self, source: Any, info: LazyInfo, **kwargs):
        log.debug(f"checking permission user_id: {info.context.user_id}")
        log.debug(f"user authenticated: {info.context.user_id is not None}")
        return info.context.user_id is not None


class OwnerPermission(sb.BasePermission):
    """Allows access to the owner of the object"""

    message = "User does not have access to object"
    error_extensions = {"code": "FORBIDDEN"}

    def has_permission(self, source: Any, info: LazyInfo, **kwargs):
        return True


class SharedPermission(sb.BasePermission):
    """Allows access to the object, if it is shared with the user"""

    message = "User does not have access to object"
    error_extensions = {"code": "FORBIDDEN"}

    def has_permission(self, source: Any, info: LazyInfo, **kwargs):
        # todo: implement logic
        return True


class SystemPermission(sb.BasePermission):
    """Allows access to the system"""

    def has_permission(self, source: Any, info: LazyInfo, **kwargs):
        # todo: implement logic
        return True


class PublicPermissions(sb.BasePermission):
    """Allow any access"""

    def has_permission(self, source: Any, info: LazyInfo, **kwargs):
        return True


class DefaultPermissions(sb.BasePermission):
    def __init__(self):
        self.auth_permission = AuthenticatedPermission()
        self.owner_permission = OwnerPermission()
        self.shared_permission = SharedPermission()
        self.system_permission = SystemPermission()

    def has_permission(self, source: Any, info: LazyInfo, **kwargs):
        log.debug("checking permission for source {}", source)
        auth = self.auth_permission.has_permission(source, info, **kwargs)
        # owner = self.owner_permission.has_permission(source, info, **kwargs)
        # shared = self.shared_permission.has_permission(source, info, **kwargs)
        # system = self.system_permission.has_permission(source, info, **kwargs)

        return auth

        # system can access any infomation
        # if system:
        #     return True

        # not authenticated
        # if not auth:
        #     return False

        # access explicitly allowed
        # if owner or shared:
        #     return True

        # deny access
        # return False
