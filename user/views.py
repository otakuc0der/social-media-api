from uuid import UUID

from rest_framework import generics, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView

from user.filters import ProfileFilter
from user.models import Follow, Profile
from user.serializers import (
    CustomAuthTokenSerializer,
    FollowerProfileSerializer,
    FollowingProfileSerializer,
    FollowSerializer,
    ProfileCreateSerializer,
    ProfileDetailSerializer,
    ProfileListSerializer,
    ProfileSerializer,
    UnfollowSerializer,
)
from user.utils.validators import (
    validate_follow_creation,
    validate_unfollow,
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

        return Response(
            {"message": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )


class ProfilesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ProfileListSerializer
    permission_classes = [IsAuthenticated]
    filterset_class = ProfileFilter

    def get_queryset(self):
        return Profile.objects.select_related(
            "user",
        )

    def get_serializer_class(self):
        if self.action == "list":
            return ProfileListSerializer

        if self.action == "follow":
            return FollowSerializer

        if self.action == "unfollow":
            return UnfollowSerializer

        if self.action == "following":
            return FollowingProfileSerializer

        if self.action == "followers":
            return FollowerProfileSerializer

        return ProfileDetailSerializer

    @action(
        detail=True,
        methods=["post"],
        url_name="follow",
        url_path="follow",
    )
    def follow(
        self,
        request: Request,
        pk: UUID | None = None,
    ) -> Response:
        current_user = request.user

        profile = self.get_object()
        user_to_follow = profile.user

        validate_follow_creation(
            follower_id=current_user.pk,
            following_id=user_to_follow.pk,
            error_factory=ValidationError,
        )

        follow = Follow.objects.create(
            follower=current_user,
            following=user_to_follow,
        )

        serializer = self.get_serializer(
            instance=follow,
        )

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )

    @action(
        detail=True,
        methods=["post"],
        url_name="unfollow",
        url_path="unfollow",
    )
    def unfollow(
        self,
        request: Request,
        pk: UUID | None = None,
    ) -> Response:
        current_user = request.user

        profile = self.get_object()
        user_to_unfollow = profile.user

        validate_unfollow(
            follower_id=current_user.pk,
            following_id=user_to_unfollow.pk,
            error_factory=ValidationError,
        )

        Follow.objects.filter(
            follower_id=current_user.pk,
            following_id=user_to_unfollow.pk,
        ).delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )

    @action(
        detail=True,
        methods=["get"],
        url_name="following",
        url_path="following",
    )
    def following(
        self,
        request: Request,
        pk: UUID | None = None,
    ) -> Response:
        current_profile = self.get_object()

        all_followings = current_profile.user.following_relations.select_related(
            "following__profile",
        )

        serializer = self.get_serializer(
            all_followings,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["get"],
        url_name="followers",
        url_path="followers",
    )
    def followers(
        self,
        request: Request,
        pk: UUID | None = None,
    ) -> Response:
        current_profile = self.get_object()

        all_followers = current_profile.user.follower_relations.select_related(
            "follower__profile",
        )

        serializer = self.get_serializer(
            all_followers,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
