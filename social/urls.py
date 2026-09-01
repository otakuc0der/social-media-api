from django.urls import path, include
from rest_framework.routers import DefaultRouter

from social.views import HashtagViewSet, PostViewSet, CommentViewSet

router = DefaultRouter()
router.register("hashtags", HashtagViewSet, basename="hashtag")
router.register("posts", PostViewSet, basename="post")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "posts/<uuid:post_pk>/comments/",
        CommentViewSet.as_view(
            {
                "get": "list",
                "post": "create"
            }
        ),
        name="comment-list"
    ),
    path(
        "posts/<uuid:post_pk>/comments/<uuid:pk>/",
        CommentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="comment-detail"
    ),
]

app_name = "social"
