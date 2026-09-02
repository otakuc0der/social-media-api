from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from social.models import Post
from user.models import Follow, Profile


class BaseSocialAPITestCase(APITestCase):
    PASSWORD = "Password123!"

    def setUp(self) -> None:
        self.user = self.create_user(
            email="anna@example.com",
            nickname="anna",
        )

        self.second_user = self.create_user(
            email="bob@example.com",
            nickname="bob",
        )

        self.third_user = self.create_user(
            email="kate@example.com",
            nickname="kate",
        )

        self.profile = self.user.profile
        self.second_profile = self.second_user.profile
        self.third_profile = self.third_user.profile

    def create_user(
        self,
        *,
        email: str,
        nickname: str,
    ):
        user = get_user_model().objects.create_user(
            email=email,
            password=self.PASSWORD,
        )

        Profile.objects.create(
            user=user,
            nickname=nickname,
        )

        return user

    def create_post(
        self,
        *,
        author=None,
        content: str = "Some post content.",
        status_value: str = Post.Status.PUBLISHED,
        scheduled_at=None,
        published_at=None,
    ) -> Post:
        if author is None:
            author = self.user

        if status_value == Post.Status.PUBLISHED and published_at is None:
            published_at = timezone.now()

        return Post.objects.create(
            author=author,
            content=content,
            status=status_value,
            scheduled_at=scheduled_at,
            published_at=published_at,
        )

    def follow(
        self,
        *,
        follower=None,
        following=None,
    ) -> Follow:
        if follower is None:
            follower = self.user

        if following is None:
            following = self.second_user

        return Follow.objects.create(
            follower=follower,
            following=following,
        )

    def authenticate(
        self,
        user=None,
    ) -> None:
        self.client.force_authenticate(
            user=user or self.user,
        )

    @staticmethod
    def get_results(response):
        if isinstance(response.data, dict) and "results" in response.data:
            return response.data["results"]

        return response.data
