from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)

from social.serializers import (
    CommentDetailSerializer,
    CommentListSerializer,
    CommentSerializer,
    HashtagSerializer,
    PostDetailSerializer,
    PostListSerializer,
    PostSerializer,
)

HASHTAG_LIST_SCHEMA = extend_schema(
    summary="List hashtags",
    description=(
        "Return a paginated list of available hashtags. "
        "Any authenticated user can retrieve hashtags."
    ),
    responses={
        200: HashtagSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    tags=["Hashtags"],
)


HASHTAG_RETRIEVE_SCHEMA = extend_schema(
    summary="Retrieve hashtag",
    description="Return information about a selected hashtag.",
    responses={
        200: HashtagSerializer,
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Hashtag not found.",
        ),
    },
    tags=["Hashtags"],
)


HASHTAG_CREATE_SCHEMA = extend_schema(
    summary="Create hashtag",
    description=(
        "Create a new hashtag. " "Only staff users are allowed to create hashtags."
    ),
    request=HashtagSerializer,
    responses={
        201: HashtagSerializer,
        400: OpenApiResponse(
            description="Invalid hashtag data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Staff permissions required.",
        ),
    },
    examples=[
        OpenApiExample(
            "Create hashtag",
            value={
                "name": "backend",
            },
            request_only=True,
        ),
    ],
    tags=["Hashtags"],
)


HASHTAG_UPDATE_SCHEMA = extend_schema(
    summary="Update hashtag",
    description=(
        "Replace the selected hashtag. "
        "Only staff users are allowed to modify hashtags."
    ),
    request=HashtagSerializer,
    responses={
        200: HashtagSerializer,
        400: OpenApiResponse(
            description="Invalid hashtag data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Staff permissions required.",
        ),
        404: OpenApiResponse(
            description="Hashtag not found.",
        ),
    },
    tags=["Hashtags"],
)


HASHTAG_PARTIAL_UPDATE_SCHEMA = extend_schema(
    summary="Partially update hashtag",
    description=(
        "Update one or more fields of the selected hashtag. "
        "Only staff users are allowed to modify hashtags."
    ),
    request=HashtagSerializer,
    responses={
        200: HashtagSerializer,
        400: OpenApiResponse(
            description="Invalid hashtag data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Staff permissions required.",
        ),
        404: OpenApiResponse(
            description="Hashtag not found.",
        ),
    },
    tags=["Hashtags"],
)


HASHTAG_DELETE_SCHEMA = extend_schema(
    summary="Delete hashtag",
    description=(
        "Delete the selected hashtag. "
        "Only staff users are allowed to delete hashtags."
    ),
    request=None,
    responses={
        204: OpenApiResponse(
            description="Hashtag deleted successfully.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Staff permissions required.",
        ),
        404: OpenApiResponse(
            description="Hashtag not found.",
        ),
    },
    tags=["Hashtags"],
)


POST_LIST_SCHEMA = extend_schema(
    summary="List available posts",
    description=(
        "Return a paginated list of posts available to the authenticated "
        "user. The response includes the user's own posts and published "
        "posts created by users they follow."
    ),
    parameters=[
        OpenApiParameter(
            name="author",
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Filter posts by author ID. Only authors available to the "
                "current user can be selected."
            ),
        ),
        OpenApiParameter(
            name="hashtags",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Filter posts by hashtag IDs. Multiple values can be "
                "provided according to django-filter conventions."
            ),
        ),
        OpenApiParameter(
            name="hashtags_names",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Comma-separated hashtag names. Return posts containing "
                "at least one of the supplied hashtags."
            ),
            examples=[
                OpenApiExample(
                    "Any hashtag",
                    value="python,django",
                ),
            ],
        ),
        OpenApiParameter(
            name="hashtags_all_names",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Comma-separated hashtag names. Return only posts "
                "containing all supplied hashtags."
            ),
            examples=[
                OpenApiExample(
                    "All hashtags",
                    value="python,django",
                ),
            ],
        ),
        OpenApiParameter(
            name="created_at_after",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter posts created on or after the supplied date.",
        ),
        OpenApiParameter(
            name="created_at_before",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter posts created on or before the supplied date.",
        ),
        OpenApiParameter(
            name="published_at_after",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter posts published on or after the supplied date.",
        ),
        OpenApiParameter(
            name="published_at_before",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter posts published on or before the supplied date.",
        ),
    ],
    responses={
        200: PostListSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    tags=["Posts"],
)


POST_CREATE_SCHEMA = extend_schema(
    summary="Create post",
    description=(
        "Create a new post for the authenticated user. "
        "A post contains text, an optional image, and optional hashtags. "
        "The author is assigned automatically from the authenticated user."
    ),
    request=PostSerializer,
    responses={
        201: PostSerializer,
        400: OpenApiResponse(
            description="Invalid post data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    examples=[
        OpenApiExample(
            "Create post",
            value={
                "content": "Working with Django REST Framework today.",
                "hashtags": [
                    "f6068635-b50e-48f9-a13b-b67ab2b18451",
                    "43589a38-494e-4b7b-b851-25a829d7db22",
                ],
            },
            request_only=True,
        ),
    ],
    tags=["Posts"],
)


POST_RETRIEVE_SCHEMA = extend_schema(
    summary="Retrieve post",
    description=(
        "Return detailed information about a selected post. "
        "The post must belong to the authenticated user or be a published "
        "post created by a user they follow."
    ),
    responses={
        200: PostDetailSerializer,
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description=(
                "Post does not exist or is not available to the current user."
            ),
            examples=[
                OpenApiExample(
                    "Unavailable post",
                    value={
                        "detail": (
                            "This post does not exist or is not " "available to you."
                        ),
                    },
                ),
            ],
        ),
    },
    tags=["Posts"],
)


POST_UPDATE_SCHEMA = extend_schema(
    summary="Update post",
    description=(
        "Replace the selected post. " "Only the author of the post can modify it."
    ),
    request=PostSerializer,
    responses={
        200: PostSerializer,
        400: OpenApiResponse(
            description="Invalid post data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Only the post author can modify this post.",
        ),
        404: OpenApiResponse(
            description="Post does not exist or is not available.",
        ),
    },
    tags=["Posts"],
)


POST_PARTIAL_UPDATE_SCHEMA = extend_schema(
    summary="Partially update post",
    description=(
        "Update one or more editable fields of the selected post. "
        "Only the author of the post can modify it."
    ),
    request=PostSerializer,
    responses={
        200: PostSerializer,
        400: OpenApiResponse(
            description="Invalid post data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Only the post author can modify this post.",
        ),
        404: OpenApiResponse(
            description="Post does not exist or is not available.",
        ),
    },
    tags=["Posts"],
)


POST_DELETE_SCHEMA = extend_schema(
    summary="Delete post",
    description=(
        "Delete the selected post. Only the author of the post " "can delete it."
    ),
    request=None,
    responses={
        204: OpenApiResponse(
            description="Post deleted successfully.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Only the post author can delete this post.",
        ),
        404: OpenApiResponse(
            description="Post does not exist or is not available.",
        ),
    },
    tags=["Posts"],
)


LIKE_POST_SCHEMA = extend_schema(
    summary="Like post",
    description=(
        "Add a like from the authenticated user to the selected post. "
        "The post must be available to the current user. "
        "The same user cannot like the same post more than once."
    ),
    request=None,
    responses={
        200: OpenApiResponse(
            description="Post liked successfully.",
            examples=[
                OpenApiExample(
                    "Successful like",
                    value={
                        "message": (
                            "daniel_codes liked post "
                            "#b777c752-aa92-4a06-a75f-a6c66a62dd3f."
                        ),
                    },
                ),
            ],
        ),
        400: OpenApiResponse(
            description="Post has already been liked by this user.",
            examples=[
                OpenApiExample(
                    "Duplicate like",
                    value={
                        "like": ["You have already liked this post."],
                    },
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Post does not exist or is not available.",
        ),
    },
    tags=["Likes"],
)


UNLIKE_POST_SCHEMA = extend_schema(
    summary="Unlike post",
    description=("Remove the authenticated user's like from the selected post."),
    request=None,
    responses={
        204: OpenApiResponse(
            description="Like removed successfully.",
        ),
        400: OpenApiResponse(
            description="The authenticated user has not liked this post.",
            examples=[
                OpenApiExample(
                    "Like does not exist",
                    value={
                        "like": [
                            "You cannot remove a like from a post "
                            "you have not liked."
                        ],
                    },
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Post does not exist or is not available.",
        ),
    },
    tags=["Likes"],
)


LIKED_POSTS_SCHEMA = extend_schema(
    summary="List liked posts",
    description=(
        "Return a paginated list of posts liked by the authenticated user. "
        "Only posts that are currently available to the user are included."
    ),
    responses={
        200: PostListSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    tags=["Likes"],
)


COMMENT_LIST_SCHEMA = extend_schema(
    summary="List post comments",
    description=(
        "Return a paginated list of comments belonging to the selected post. "
        "The parent post must be available to the authenticated user."
    ),
    parameters=[
        OpenApiParameter(
            name="author",
            type=int,
            location=OpenApiParameter.QUERY,
            required=False,
            description="Filter comments by author ID.",
        ),
        OpenApiParameter(
            name="created_at_after",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=("Return comments created on or after the supplied date."),
        ),
        OpenApiParameter(
            name="created_at_before",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=("Return comments created on or before the supplied date."),
        ),
    ],
    responses={
        200: CommentListSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Parent post does not exist or is not available.",
        ),
    },
    tags=["Comments"],
)


COMMENT_CREATE_SCHEMA = extend_schema(
    summary="Create comment",
    description=(
        "Add a comment to the selected post. "
        "The author and parent post are assigned automatically."
    ),
    request=CommentSerializer,
    responses={
        201: CommentSerializer,
        400: OpenApiResponse(
            description="Invalid comment data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Parent post does not exist or is not available.",
        ),
    },
    examples=[
        OpenApiExample(
            "Create comment",
            value={
                "content": "Great post!",
            },
            request_only=True,
        ),
    ],
    tags=["Comments"],
)


COMMENT_RETRIEVE_SCHEMA = extend_schema(
    summary="Retrieve comment",
    description=(
        "Return detailed information about a selected comment belonging "
        "to the selected post."
    ),
    responses={
        200: CommentDetailSerializer,
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Post or comment not found.",
        ),
    },
    tags=["Comments"],
)


COMMENT_UPDATE_SCHEMA = extend_schema(
    summary="Update comment",
    description=(
        "Replace the selected comment. " "Only the comment author can modify it."
    ),
    request=CommentSerializer,
    responses={
        200: CommentSerializer,
        400: OpenApiResponse(
            description="Invalid comment data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Only the comment author can modify this comment.",
        ),
        404: OpenApiResponse(
            description="Post or comment not found.",
        ),
    },
    tags=["Comments"],
)


COMMENT_PARTIAL_UPDATE_SCHEMA = extend_schema(
    summary="Partially update comment",
    description=(
        "Update one or more editable fields of the selected comment. "
        "Only the comment author can modify it."
    ),
    request=CommentSerializer,
    responses={
        200: CommentSerializer,
        400: OpenApiResponse(
            description="Invalid comment data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Only the comment author can modify this comment.",
        ),
        404: OpenApiResponse(
            description="Post or comment not found.",
        ),
    },
    tags=["Comments"],
)


COMMENT_DELETE_SCHEMA = extend_schema(
    summary="Delete comment",
    description=(
        "Delete the selected comment. " "Only the comment author can delete it."
    ),
    request=None,
    responses={
        204: OpenApiResponse(
            description="Comment deleted successfully.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        403: OpenApiResponse(
            description="Only the comment author can delete this comment.",
        ),
        404: OpenApiResponse(
            description="Post or comment not found.",
        ),
    },
    tags=["Comments"],
)
