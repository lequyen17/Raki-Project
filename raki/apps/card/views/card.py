from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from core.utils.openapi_common import ErrorResponseSerializer
from apps.card.serializers import (
    CardDetailResponseSerializer,
    CardUpdateSerializer,
    ReviewCardResponseSerializer,
    ReviewCardSerializer,
)
from apps.card.services.main_service import CardMainService


@extend_schema(
    tags=["Cards"],
    summary="Chấm điểm khi review thẻ",
    request=ReviewCardSerializer,
    responses={
        200: ReviewCardResponseSerializer,
        400: ErrorResponseSerializer,
        404: ErrorResponseSerializer,
    },
)
class ReviewCardView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, card_id):
        serializer = ReviewCardSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = CardMainService.review_card(
            card_id, request.user, serializer.validated_data
        )
        return ApiResponse(data=data, message="Card reviewed successfully")


@extend_schema_view(
    get=extend_schema(
        tags=["Cards"],
        summary="Chi tiết thẻ",
        responses={
            200: CardDetailResponseSerializer,
            404: ErrorResponseSerializer,
        },
    ),
    put=extend_schema(
        tags=["Cards"],
        summary="Cập nhật thẻ",
        request=CardUpdateSerializer,
        responses={
            200: CardDetailResponseSerializer,
            400: ErrorResponseSerializer,
            404: ErrorResponseSerializer,
        },
    ),
    delete=extend_schema(
        tags=["Cards"],
        summary="Xóa thẻ",
        responses={
            200: {"type": "object", "properties": {"success": {"type": "boolean"}}},
            404: ErrorResponseSerializer,
        },
    ),
)
class CardDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, card_id):
        data = CardMainService.get_card_detail(card_id, request.user)
        return ApiResponse(data=data)

    def put(self, request, card_id):
        serializer = CardUpdateSerializer(
            data=request.data, context={"card_id": card_id, "user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        data = CardMainService.update_card(
            card_id, request.user, serializer.validated_data["field_values"]
        )
        return ApiResponse(data=data, message="Card updated successfully")

    def delete(self, request, card_id):
        data = CardMainService.delete_card(card_id, request.user)
        return ApiResponse(data=data, message="Card deleted successfully")
