from rest_framework.permissions import (SAFE_METHODS, BasePermission,
                                        IsAuthenticatedOrReadOnly)


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        )


class IsAuthorAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view)
            or (request.method == 'POST' and request.user.is_authenticated)
        )

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or obj.author == request.user:
            return True
        return super().has_object_permission(request, view, obj)


class IsAuthUserOrAdminOrReadOnly(IsAuthenticatedOrReadOnly):
    def has_object_permission(self, request, view, obj):
        return (
            super().has_object_permission(request, view, obj)
            or (request.user == obj and request.method != 'DELETE')
        )