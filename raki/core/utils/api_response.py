from rest_framework import status as http_status
from rest_framework.response import Response


class ApiResponse(Response):

    def __init__(
        self,
        data=None,
        message="Success",
        status="success",
        status_code=http_status.HTTP_200_OK,
    ):
        super().__init__(
            {
                "status": status,
                "message": message,
                "data": data,
            },
            status=status_code,
        )
