from rest_framework.permissions import (
    SAFE_METHODS,
    BasePermission,
)
from rest_framework.request import Request


class IsAdminOrReadOnly(BasePermission):
    def has_permission(
        self,
        request: Request,
        view,
    ) -> bool:
        if request.user.is_authenticated and request.method in SAFE_METHODS:
            return True

        return bool(
            request.user.is_authenticated
            and request.user.is_staff
        )


class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return obj.author == request.user
