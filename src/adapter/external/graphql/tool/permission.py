from typing import Any

import strawberry as sb


class AuthenticatedPermission(sb.BasePermission):
    """Denies access to unauthenticated users"""

    def has_permission(self, source: Any, info: sb.Info, **kwargs):
        # todo implement logic
        return True


class OwnerPermission(sb.BasePermission):
    """Allows access to the owner of the object"""

    def has_permission(self, source: Any, info: sb.Info, **kwargs):
        # todo: implement logic
        return True


class SharedPermission(sb.BasePermission):
    """Allows access to the object, if it is shared with the user"""

    def has_permission(self, source: Any, info: sb.Info, **kwargs):
        # todo: implement logic
        return True


class SystemPermission(sb.BasePermission):
    """Allows access to the system"""

    def has_permission(self, source: Any, info: sb.Info, **kwargs):
        # todo: implement logic
        return True


class PublicPermissions(sb.BasePermission):
    """Allow any access"""

    def has_permission(self, source: Any, info: sb.Info, **kwargs):
        return True


class DefaultPermissions(sb.BasePermission):
    def __init__(self):
        self.auth_permission = AuthenticatedPermission()
        self.owner_permission = OwnerPermission()
        self.shared_permission = SharedPermission()
        self.system_permission = SystemPermission()

    def has_permission(self, source: Any, info: sb.Info, **kwargs):
        auth = self.auth_permission.has_permission(source, info, **kwargs)
        owner = self.owner_permission.has_permission(source, info, **kwargs)
        shared = self.shared_permission.has_permission(source, info, **kwargs)
        system = self.system_permission.has_permission(source, info, **kwargs)

        # system can access any infomation
        if system:
            return True

        # not authenticated
        if not auth:
            return False

        # access explicitly allowed
        if owner or shared:
            return True

        # deny access
        return False
