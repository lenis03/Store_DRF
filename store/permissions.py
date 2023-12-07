from rest_framework import permissions

CREATE_RETRIEVE_METHOD = ('GET', 'POST')


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in permissions.SAFE_METHODS
            or
            (request.user and request.user.is_staff)
            )


class SendPrivateEmailToCustomerPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and
            request.user.has_perm('store.send_private_email')
            )


class IsAdminOrCreateAndRetrieve(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.method in CREATE_RETRIEVE_METHOD
            or
            (request.user and request.user.is_staff))
