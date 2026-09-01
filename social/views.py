from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from social.filters import PostFilter, CommentFilter
from social.models import Comment, Hashtag, Like, Post
from social.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from social.serializers import (
    CommentDetailSerializer,
    CommentListSerializer,
    CommentSerializer,
    EmptySerializer,
    HashtagSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostSerializer,
)
from social.utils.helpers import get_available_posts_for_user
from social.utils.validators import (
    validate_like_creation,
    validate_like_removal,
)


class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [IsAdminOrReadOnly]


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        IsAuthenticated,
        IsAuthorOrReadOnly,
    ]
    filterset_class = PostFilter

    def get_queryset(self) -> QuerySet[Post]:
        queryset = (
            Post.objects
            .select_related("author__profile")
            .prefetch_related("hashtags")
        )

        return get_available_posts_for_user(
            self.request.user,
            queryset,
        )

    def get_object(self) -> Post:
        try:
            return super().get_object()
        except Http404:
            raise NotFound("This post does not exist or is not available to you.")

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action in (
            "list",
            "list_liked_posts",
        ):
            return PostListSerializer

        if self.action == "retrieve":
            return PostDetailSerializer

        if self.action in (
            "add_like",
            "remove_like",
        ):
            return EmptySerializer

        return PostSerializer

    def perform_create(
        self,
        serializer: BaseSerializer,
    ) -> None:
        serializer.save(
            author=self.request.user,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="like",
        url_name="add-like",
        permission_classes=[IsAuthenticated],
    )
    def add_like(
        self,
        request: Request,
        pk: str | None = None,
    ) -> Response:
        current_user = request.user
        post = self.get_object()

        validate_like_creation(
            user_id=current_user.pk,
            post_id=post.pk,
            error_factory=ValidationError,
        )

        Like.objects.create(
            user=current_user,
            post=post,
        )

        return Response(
            {
                "message": (
                    f"{current_user.profile.nickname} " f"liked post #{post.pk}."
                )
            },
            status=HTTP_200_OK,
        )

    @action(
        detail=True,
        methods=["post"],
        url_path="unlike",
        url_name="remove-like",
        permission_classes=[IsAuthenticated],
    )
    def remove_like(
        self,
        request: Request,
        pk: str | None = None,
    ) -> Response:
        current_user = request.user
        post = self.get_object()

        validate_like_removal(
            user_id=current_user.pk,
            post_id=post.pk,
            error_factory=ValidationError,
        )

        Like.objects.filter(
            user=current_user,
            post=post,
        ).delete()

        return Response(
            status=HTTP_204_NO_CONTENT,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="liked-posts",
        url_name="liked-posts",
    )
    def list_liked_posts(
        self,
        request: Request,
    ) -> Response:
        liked_posts = self.get_queryset().filter(
            likes__user=request.user,
        )

        page = self.paginate_queryset(liked_posts)

        if page is not None:
            serializer = self.get_serializer(
                page,
                many=True,
            )
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(
            liked_posts,
            many=True,
        )

        return Response(
            serializer.data,
            status=HTTP_200_OK,
        )


class CommentViewSet(viewsets.ModelViewSet):
    permission_classes = [
        IsAuthenticated,
        IsAuthorOrReadOnly,
    ]
    filterset_class = CommentFilter

    def get_serializer_class(self) -> type[BaseSerializer]:
        if self.action == "list":
            return CommentListSerializer

        if self.action == "retrieve":
            return CommentDetailSerializer

        return CommentSerializer

    def get_queryset(self) -> QuerySet[Comment]:
        available_posts = get_available_posts_for_user(
            self.request.user, Post.objects.all()
        )
        post = get_object_or_404(available_posts, pk=self.kwargs["post_pk"])
        return Comment.objects.select_related("author__profile", "post").filter(
            post=post
        )

    def perform_create(
        self,
        serializer: BaseSerializer,
    ) -> None:
        available_posts = get_available_posts_for_user(
            self.request.user,
            Post.objects.all(),
        )

        post = get_object_or_404(
            available_posts,
            pk=self.kwargs["post_pk"],
        )

        serializer.save(
            author=self.request.user,
            post=post,
        )
