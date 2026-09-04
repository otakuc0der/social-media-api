from uuid import UUID

from drf_spectacular.utils import extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework.views import APIView
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser

from user.filters import ProfileFilter
from user.models import Follow, Profile
from user.schema import (
    CURRENT_PROFILE_DELETE_SCHEMA,
    CURRENT_PROFILE_PARTIAL_UPDATE_SCHEMA,
    CURRENT_PROFILE_RETRIEVE_SCHEMA,
    CURRENT_PROFILE_UPDATE_SCHEMA,
    FOLLOW_PROFILE_SCHEMA,
    FOLLOWERS_LIST_SCHEMA,
    FOLLOWING_LIST_SCHEMA,
    LOGIN_SCHEMA,
    LOGOUT_SCHEMA,
    PROFILE_LIST_SCHEMA,
    PROFILE_RETRIEVE_SCHEMA,
    REGISTER_SCHEMA,
    UNFOLLOW_PROFILE_SCHEMA,
)
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


@extend_schema_view(
    post=LOGIN_SCHEMA,
)
class CreateTokenView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = CustomAuthTokenSerializer


@extend_schema_view(
    create=REGISTER_SCHEMA,
)
class CreateUserView(generics.CreateAPIView):
    serializer_class = ProfileCreateSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    retrieve=CURRENT_PROFILE_RETRIEVE_SCHEMA,
    update=CURRENT_PROFILE_UPDATE_SCHEMA,
    partial_update=CURRENT_PROFILE_PARTIAL_UPDATE_SCHEMA,
    destroy=CURRENT_PROFILE_DELETE_SCHEMA,
)
class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]

    def get_object(self) -> Profile:
        return self.request.user.profile

    def destroy(
        self,
        request: Request,
        *args,
        **kwargs,
    ) -> Response:
        user = request.user
        user.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )


@extend_schema_view(
    post=LOGOUT_SCHEMA,
)
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(
        self,
        request: Request,
    ) -> Response:
        request.user.auth_token.delete()

        return Response(
            {
                "message": "Logged out successfully",
            },
            status=status.HTTP_200_OK,
        )


@extend_schema_view(
    list=PROFILE_LIST_SCHEMA,
    retrieve=PROFILE_RETRIEVE_SCHEMA,
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

    @FOLLOW_PROFILE_SCHEMA
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

    @UNFOLLOW_PROFILE_SCHEMA
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

    @FOLLOWING_LIST_SCHEMA
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

        page = self.paginate_queryset(
            all_followings,
        )

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )

            return self.get_paginated_response(
                serializer.data,
            )

        serializer = self.get_serializer(
            all_followings,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    @FOLLOWERS_LIST_SCHEMA
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

        page = self.paginate_queryset(
            all_followers,
        )

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )

            return self.get_paginated_response(
                serializer.data,
            )

        serializer = self.get_serializer(
            all_followers,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
