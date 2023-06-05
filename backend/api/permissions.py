from rest_framework import permissions


class IsUserOwner(permissions.BasePermission):
    """Доступ только автору"""
    message = 'Изменение чужого рецепта запрещено'

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return (request.user.is_authenticated
                and obj.author == request.user
                )
