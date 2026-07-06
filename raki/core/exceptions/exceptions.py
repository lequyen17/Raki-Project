from rest_framework import status


class AppException(Exception):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Application error"

    def __init__(self, message=None):
        if message:
            self.message = message


class NotFoundException(AppException):
    status_code = status.HTTP_404_NOT_FOUND
    message = "Resource not found"


class BadRequestException(AppException):
    status_code = status.HTTP_400_BAD_REQUEST
    message = "Bad request"


class ConflictException(AppException):
    status_code = status.HTTP_409_CONFLICT
    message = "Conflict"


class PermissionDeniedException(AppException):
    status_code = status.HTTP_403_FORBIDDEN
    message = "Permission denied"


class UnauthorizedException(AppException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message = "Unauthorized"


class PaymentRequiredException(AppException):
    status_code = 402
    message = "Payment required"


class InternalServerException(AppException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    message = "Internal server error"
