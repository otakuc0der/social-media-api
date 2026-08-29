from uuid import uuid4

from django.urls import reverse
from rest_framework import status

from user.tests.base import BaseUserAPITestCase


class ProfileListViewTests(BaseUserAPITestCase):
    def setUp(self) -> None:
        self.url = reverse(
            "user:profile-list",
        )

    def test_profile_list_requires_authentication(self) -> None:
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_profile_list_returns_profiles(self) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        nicknames = {
            item["nickname"]
            for item in response.data["results"]
        }

        self.assertIn(
            "anna",
            nicknames,
        )
        self.assertIn(
            "bob",
            nicknames,
        )
        self.assertIn(
            "kate",
            nicknames,
        )

    def test_profile_list_contains_current_user(self) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
        )

        ids = {
            item["id"]
            for item in response.data["results"]
        }

        self.assertIn(
            str(self.profile.pk),
            ids,
        )

    def test_filter_by_nickname(self) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
            {
                "nickname": "bo",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )
        self.assertEqual(
            response.data["results"][0]["nickname"],
            "bob",
        )

    def test_filter_by_nickname_is_case_insensitive(self) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
            {
                "nickname": "BOB",
            },
        )

        self.assertEqual(
            response.data["results"][0]["nickname"],
            "bob",
        )

    def test_filter_by_email(self) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
            {
                "email": "bob@",
            },
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )
        self.assertEqual(
            response.data["results"][0]["nickname"],
            "bob",
        )

    def test_filter_by_first_name(self) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
            {
                "first_name": "kat",
            },
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )
        self.assertEqual(
            response.data["results"][0]["nickname"],
            "kate",
        )

    def test_filter_by_last_name(self) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
            {
                "last_name": "brown",
            },
        )

        self.assertEqual(
            len(response.data["results"]),
            1,
        )
        self.assertEqual(
            response.data["results"][0]["nickname"],
            "bob",
        )


class ProfileDetailViewTests(BaseUserAPITestCase):
    def test_retrieve_profile(self) -> None:
        self.authenticate()

        url = reverse(
            "user:profile-detail",
            args=[self.second_profile.pk],
        )

        response = self.client.get(
            url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["id"],
            str(self.second_profile.pk),
        )
        self.assertEqual(
            response.data["nickname"],
            "bob",
        )

    def test_retrieve_own_profile_by_id(self) -> None:
        self.authenticate()

        url = reverse(
            "user:profile-detail",
            args=[self.profile.pk],
        )

        response = self.client.get(
            url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data["id"],
            str(self.profile.pk),
        )

    def test_retrieve_profile_requires_authentication(self) -> None:
        url = reverse(
            "user:profile-detail",
            args=[self.second_profile.pk],
        )

        response = self.client.get(
            url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_retrieve_unknown_profile_returns_404(self) -> None:
        self.authenticate()

        url = reverse(
            "user:profile-detail",
            args=[uuid4()],
        )

        response = self.client.get(
            url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )
