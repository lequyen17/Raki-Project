from rest_framework.views import exception_handler

from core.utils.api_response import ApiResponse
from core.exceptions.exceptions import AppException


def first_validation_error(errors):
    if isinstance(errors, list):
        return str(errors[0])

    if isinstance(errors, dict):
        for value in errors.values():
            return first_validation_error(value)

    return str(errors)


def custom_exception_handler(exc, context):

    # Custom exception
    if isinstance(exc, AppException):
        return ApiResponse(
            status="error",
            message=exc.message,
            data=None,
            status_code=exc.status_code,
        )

    # ValidationError, AuthenticationFailed,...
    response = exception_handler(exc, context)

    if response is not None:

        return ApiResponse(
            status="error",
            message=first_validation_error(response.data),
            data=None,
            status_code=response.status_code,
        )

    # Unknown error
    return ApiResponse(
        status="error",
        message="Internal server error",
        data=None,
        status_code=500,
    )
