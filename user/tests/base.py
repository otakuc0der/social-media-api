from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from user.models import Profile


class BaseUserAPITestCase(APITestCase):
    PASSWORD = "Password123!"

    def setUp(self) -> None:
        self.user = self.create_user(
            email="anna@example.com",
            first_name="Anna",
            last_name="Smith",
            nickname="anna",
        )

        self.second_user = self.create_user(
            email="bob@example.com",
            first_name="Bob",
            last_name="Brown",
            nickname="bob",
        )

        self.third_user = self.create_user(
            email="kate@example.com",
            first_name="Kate",
            last_name="Wilson",
            nickname="kate",
        )

        self.profile = self.user.profile
        self.second_profile = self.second_user.profile
        self.third_profile = self.third_user.profile

    def create_user(
        self,
        *,
        email: str,
        first_name: str = "",
        last_name: str = "",
        nickname: str,
    ):
        user = get_user_model().objects.create_user(
            email=email,
            password=self.PASSWORD,
            first_name=first_name,
            last_name=last_name,
        )

        Profile.objects.create(
            user=user,
            nickname=nickname,
        )

        return user

    def authenticate(
        self,
        user=None,
    ) -> None:
        self.client.force_authenticate(
            user=user or self.user,
        )
