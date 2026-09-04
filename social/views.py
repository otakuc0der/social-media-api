from django.db import transaction
from django.db.models import QuerySet
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema_view
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import BaseSerializer
from rest_framework.status import HTTP_200_OK, HTTP_204_NO_CONTENT

from social.filters import CommentFilter, PostFilter
from social.models import Comment, Hashtag, Like, Post
from social.permissions import IsAdminOrReadOnly, IsAuthorOrReadOnly
from social.schema import (
    COMMENT_CREATE_SCHEMA,
    COMMENT_DELETE_SCHEMA,
    COMMENT_LIST_SCHEMA,
    COMMENT_PARTIAL_UPDATE_SCHEMA,
    COMMENT_RETRIEVE_SCHEMA,
    COMMENT_UPDATE_SCHEMA,
    HASHTAG_CREATE_SCHEMA,
    HASHTAG_DELETE_SCHEMA,
    HASHTAG_LIST_SCHEMA,
    HASHTAG_PARTIAL_UPDATE_SCHEMA,
    HASHTAG_RETRIEVE_SCHEMA,
    HASHTAG_UPDATE_SCHEMA,
    LIKED_POSTS_SCHEMA,
    LIKE_POST_SCHEMA,
    POST_CREATE_SCHEMA,
    POST_DELETE_SCHEMA,
    POST_LIST_SCHEMA,
    POST_PARTIAL_UPDATE_SCHEMA,
    POST_RETRIEVE_SCHEMA,
    POST_UPDATE_SCHEMA,
    UNLIKE_POST_SCHEMA,
)
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
from social.tasks import publish_post
from social.utils.helpers import get_available_posts_for_user
from social.utils.validators import (
    validate_like_creation,
    validate_like_removal,
)


@extend_schema_view(
    list=HASHTAG_LIST_SCHEMA,
    retrieve=HASHTAG_RETRIEVE_SCHEMA,
    create=HASHTAG_CREATE_SCHEMA,
    update=HASHTAG_UPDATE_SCHEMA,
    partial_update=HASHTAG_PARTIAL_UPDATE_SCHEMA,
    destroy=HASHTAG_DELETE_SCHEMA,
)
class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [IsAdminOrReadOnly]


@extend_schema_view(
    list=POST_LIST_SCHEMA,
    create=POST_CREATE_SCHEMA,
    retrieve=POST_RETRIEVE_SCHEMA,
    update=POST_UPDATE_SCHEMA,
    partial_update=POST_PARTIAL_UPDATE_SCHEMA,
    destroy=POST_DELETE_SCHEMA,
)
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [
        IsAuthenticated,
        IsAuthorOrReadOnly,
    ]
    parser_classes = [
        MultiPartParser,
        FormParser,
        JSONParser,
    ]
    filterset_class = PostFilter

    def get_queryset(self) -> QuerySet[Post]:
        queryset = Post.objects.select_related(
            "author__profile",
        ).prefetch_related(
            "hashtags",
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
        scheduled_at = serializer.validated_data.get("scheduled_at")

        if not scheduled_at:
            serializer.save(
                author=self.request.user,
                status=Post.Status.PUBLISHED,
                published_at=timezone.now(),
            )
        else:
            post = serializer.save(
                author=self.request.user,
                status=Post.Status.SCHEDULED,
                published_at=None
            )

            transaction.on_commit(
                lambda: publish_post.apply_async(
                    args=[str(post.pk)],
                    eta=scheduled_at,
                )
            )

    @LIKE_POST_SCHEMA
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
                ),
            },
            status=HTTP_200_OK,
        )

    @UNLIKE_POST_SCHEMA
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

    @LIKED_POSTS_SCHEMA
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
        liked_posts = self.filter_queryset(
            self.get_queryset().filter(
                likes__user=request.user,
            )
        )

        page = self.paginate_queryset(
            liked_posts,
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
            liked_posts,
            many=True,
        )

        return Response(
            serializer.data,
            status=HTTP_200_OK,
        )


@extend_schema_view(
    list=COMMENT_LIST_SCHEMA,
    create=COMMENT_CREATE_SCHEMA,
    retrieve=COMMENT_RETRIEVE_SCHEMA,
    update=COMMENT_UPDATE_SCHEMA,
    partial_update=COMMENT_PARTIAL_UPDATE_SCHEMA,
    destroy=COMMENT_DELETE_SCHEMA,
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
            self.request.user,
            Post.objects.all(),
        )

        post = get_object_or_404(
            available_posts,
            pk=self.kwargs["post_pk"],
        )

        return Comment.objects.select_related(
            "author__profile",
            "post",
        ).filter(
            post=post,
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
