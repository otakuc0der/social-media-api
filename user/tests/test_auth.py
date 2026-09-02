from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.authtoken.models import Token

from user.models import Profile
from user.tests.base import BaseUserAPITestCase


class CreateUserViewTests(BaseUserAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.url = reverse(
            "user:create",
        )

    def test_register_creates_user_and_profile(
        self,
    ) -> None:
        payload = {
            "email": "new@example.com",
            "password": "NewPassword123!",
            "nickname": "new_user",
            "first_name": "New",
            "last_name": "User",
            "bio": "New bio",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = get_user_model().objects.get(
            email="new@example.com",
        )

        self.assertEqual(
            user.profile.nickname,
            "new_user",
        )

        self.assertTrue(
            user.check_password(
                payload["password"],
            )
        )

    def test_register_hashes_password(
        self,
    ) -> None:
        payload = {
            "email": "new@example.com",
            "password": "NewPassword123!",
            "nickname": "new_user",
        }

        response = self.client.post(
            self.url,
            payload,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        user = get_user_model().objects.get(
            email=payload["email"],
        )

        self.assertNotEqual(
            user.password,
            payload["password"],
        )

        self.assertTrue(
            user.check_password(
                payload["password"],
            )
        )

    def test_register_rejects_duplicate_email(
        self,
    ) -> None:
        response = self.client.post(
            self.url,
            {
                "email": self.user.email,
                "password": "NewPassword123!",
                "nickname": "another",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_register_rejects_duplicate_nickname(
        self,
    ) -> None:
        response = self.client.post(
            self.url,
            {
                "email": "new@example.com",
                "password": "NewPassword123!",
                "nickname": self.profile.nickname,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class CreateTokenViewTests(BaseUserAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.url = reverse(
            "user:login",
        )

    def test_login_returns_token(
        self,
    ) -> None:
        response = self.client.post(
            self.url,
            {
                "email": self.user.email,
                "password": self.PASSWORD,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertIn(
            "token",
            response.data,
        )

        self.assertTrue(
            Token.objects.filter(
                user=self.user,
                key=response.data["token"],
            ).exists()
        )

    def test_login_rejects_wrong_password(
        self,
    ) -> None:
        response = self.client.post(
            self.url,
            {
                "email": self.user.email,
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_login_rejects_unknown_email(
        self,
    ) -> None:
        response = self.client.post(
            self.url,
            {
                "email": "unknown@example.com",
                "password": self.PASSWORD,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )


class LogoutViewTests(BaseUserAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.url = reverse(
            "user:logout",
        )

    def test_logout_deletes_token(
        self,
    ) -> None:
        token = Token.objects.create(
            user=self.user,
        )

        self.client.credentials(
            HTTP_AUTHORIZATION=(f"Token {token.key}"),
        )

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertFalse(
            Token.objects.filter(
                user=self.user,
            ).exists()
        )

    def test_logout_requires_authentication(
        self,
    ) -> None:
        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class ManageUserViewTests(BaseUserAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.url = reverse(
            "user:manage",
        )

    def test_retrieve_own_profile(
        self,
    ) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            response.data["nickname"],
            self.profile.nickname,
        )

    def test_manage_requires_authentication(
        self,
    ) -> None:
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_update_profile(
        self,
    ) -> None:
        self.authenticate()

        response = self.client.patch(
            self.url,
            {
                "nickname": "updated_anna",
                "bio": "Updated bio",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.profile.refresh_from_db()

        self.assertEqual(
            self.profile.nickname,
            "updated_anna",
        )

        self.assertEqual(
            self.profile.bio,
            "Updated bio",
        )

    def test_update_email(
        self,
    ) -> None:
        self.authenticate()

        response = self.client.patch(
            self.url,
            {
                "email": "updated@example.com",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertEqual(
            self.user.email,
            "updated@example.com",
        )

    def test_update_rejects_existing_email(
        self,
    ) -> None:
        self.authenticate()

        response = self.client.patch(
            self.url,
            {
                "email": self.second_user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_update_allows_current_email(
        self,
    ) -> None:
        self.authenticate()

        response = self.client.patch(
            self.url,
            {
                "email": self.user.email,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

    def test_update_password_hashes_password(
        self,
    ) -> None:
        self.authenticate()

        new_password = "NewPassword456!"

        response = self.client.patch(
            self.url,
            {
                "password": new_password,
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.user.refresh_from_db()

        self.assertNotEqual(
            self.user.password,
            new_password,
        )

        self.assertTrue(
            self.user.check_password(
                new_password,
            )
        )

    def test_delete_profile_deletes_user_account(
        self,
    ) -> None:
        self.authenticate()

        user_pk = self.user.pk
        profile_pk = self.profile.pk

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            get_user_model()
            .objects.filter(
                pk=user_pk,
            )
            .exists()
        )

        self.assertFalse(
            Profile.objects.filter(
                pk=profile_pk,
            ).exists()
        )
