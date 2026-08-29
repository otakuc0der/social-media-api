from rest_framework import generics, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from user.filters import ProfileFilter
from user.models import Profile
from user.serializers import (
    CustomAuthTokenSerializer,
    ProfileSerializer,
    ProfileCreateSerializer,
    ProfileListSerializer, ProfileDetailSerializer,
)


class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = CustomAuthTokenSerializer


class CreateUserView(generics.CreateAPIView):
    serializer_class = ProfileCreateSerializer
    permission_classes = [AllowAny]


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self) -> Profile:
        return self.request.user.profile


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request: Request) -> Response:
        request.user.auth_token.delete()
        return Response({"message": "Logged out successfully"}, status=200)


class ProfilesReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Profile.objects.select_related("user")
    serializer_class = ProfileListSerializer
    permission_classes = [AllowAny]
    filterset_class = ProfileFilter

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer
        return ProfileDetailSerializer
