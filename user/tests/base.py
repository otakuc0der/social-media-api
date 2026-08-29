from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from user.models import Profile


class BaseUserAPITestCase(APITestCase):
    PASSWORD = "TestPassword123!"

    @classmethod
    def setUpTestData(cls) -> None:
        user_model = get_user_model()

        cls.user = user_model.objects.create_user(
            email="anna@example.com",
            password=cls.PASSWORD,
            first_name="Anna",
            last_name="Smith",
        )
        cls.profile = Profile.objects.create(
            user=cls.user,
            nickname="anna",
            bio="Anna bio",
        )

        cls.second_user = user_model.objects.create_user(
            email="bob@example.com",
            password=cls.PASSWORD,
            first_name="Bob",
            last_name="Brown",
        )
        cls.second_profile = Profile.objects.create(
            user=cls.second_user,
            nickname="bob",
            bio="Bob bio",
        )

        cls.third_user = user_model.objects.create_user(
            email="kate@example.com",
            password=cls.PASSWORD,
            first_name="Kate",
            last_name="White",
        )
        cls.third_profile = Profile.objects.create(
            user=cls.third_user,
            nickname="kate",
            bio="Kate bio",
        )

    def authenticate(self, user=None) -> None:
        self.client.force_authenticate(
            user=user or self.user,
        )
