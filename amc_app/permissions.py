from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            getattr(request.user, 'is_active', False)
            and getattr(request.user, 'role', None) == 'super_admin'
        )


class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return (
            getattr(request.user, 'is_active', False)
            and getattr(request.user, 'role', None) in ['super_admin', 'admin']
        )


class IsAuthenticatedTblUser(BasePermission):
    def has_permission(self, request, view):
        return getattr(request.user, 'is_active', False)