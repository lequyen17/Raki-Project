from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from core.utils.api_response import ApiResponse
from apps.deck.serializers import UserSearchResponseSerializer
from apps.deck.services import DeckService


@extend_schema(
    tags=["Decks"],
    summary="Tìm kiếm user theo username",
    responses={200: UserSearchResponseSerializer},
)
class SearchUsersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "")
        data = DeckService.search_users(query, request.user)
        return ApiResponse(data=data)
