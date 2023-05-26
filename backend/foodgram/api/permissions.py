from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or (request.user.is_authenticated and request.user.is_admin)
        ) 


class IsAuthorAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (request.user.is_superuser
                 or obj.author == request.user
                 or request.method == 'POST')
        )


class IsAuthUserOrAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return True

    def has_object_permission(self, request, view, obj):
        return (
            request.method in ('GET',)
            or (request.user == obj)
            or request.user.is_admin
        )
