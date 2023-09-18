from rest_framework.permissions import BasePermission, SAFE_METHODS


class OwnerOrRO(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        if obj.author == request.user:
            return True
        return False


class AdminOrRO(BasePermission):
    def has_object_permission(self, request, view, obj):
        return True

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if request.user and request.user.is_staff:
            return True
        return False
