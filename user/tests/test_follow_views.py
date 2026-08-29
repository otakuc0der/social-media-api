from uuid import uuid4

from django.urls import reverse
from rest_framework import status

from user.models import Follow
from user.tests.base import BaseUserAPITestCase


class FollowProfileViewTests(BaseUserAPITestCase):
    def setUp(self) -> None:
        self.url = reverse(
            "user:profile-follow",
            args=[self.second_profile.pk],
        )

    def test_follow_profile(self) -> None:
        self.authenticate()

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Follow.objects.filter(
                follower=self.user,
                following=self.second_user,
            ).exists()
        )

    def test_follow_response_contains_users(self) -> None:
        self.authenticate()

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.data["follower"],
            "anna",
        )
        self.assertEqual(
            response.data["following"],
            "bob",
        )

    def test_follow_requires_authentication(self) -> None:
        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_cannot_follow_yourself(self) -> None:
        self.authenticate()

        url = reverse(
            "user:profile-follow",
            args=[self.profile.pk],
        )

        response = self.client.post(
            url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertFalse(
            Follow.objects.filter(
                follower=self.user,
                following=self.user,
            ).exists()
        )

    def test_cannot_follow_same_profile_twice(self) -> None:
        Follow.objects.create(
            follower=self.user,
            following=self.second_user,
        )

        self.authenticate()

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Follow.objects.filter(
                follower=self.user,
                following=self.second_user,
            ).count(),
            1,
        )

    def test_follow_unknown_profile_returns_404(self) -> None:
        self.authenticate()

        url = reverse(
            "user:profile-follow",
            args=[uuid4()],
        )

        response = self.client.post(
            url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


class UnfollowProfileViewTests(BaseUserAPITestCase):
    def setUp(self) -> None:
        self.url = reverse(
            "user:profile-unfollow",
            args=[self.second_profile.pk],
        )

    def test_unfollow_profile(self) -> None:
        Follow.objects.create(
            follower=self.user,
            following=self.second_user,
        )

        self.authenticate()

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Follow.objects.filter(
                follower=self.user,
                following=self.second_user,
            ).exists()
        )

    def test_unfollow_requires_authentication(self) -> None:
        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_cannot_unfollow_yourself(self) -> None:
        self.authenticate()

        url = reverse(
            "user:profile-unfollow",
            args=[self.profile.pk],
        )

        response = self.client.post(
            url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_cannot_unfollow_profile_not_followed(self) -> None:
        self.authenticate()

        response = self.client.post(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_unfollow_unknown_profile_returns_404(self) -> None:
        self.authenticate()

        url = reverse(
            "user:profile-unfollow",
            args=[uuid4()],
        )

        response = self.client.post(
            url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )


class FollowingProfilesViewTests(BaseUserAPITestCase):
    def setUp(self) -> None:
        self.url = reverse(
            "user:profile-following",
            args=[self.profile.pk],
        )

    def test_following_returns_profiles_user_follows(self) -> None:
        Follow.objects.create(
            follower=self.user,
            following=self.second_user,
        )
        Follow.objects.create(
            follower=self.user,
            following=self.third_user,
        )

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
            for item in response.data
        }

        self.assertEqual(
            nicknames,
            {
                "bob",
                "kate",
            },
        )

    def test_following_does_not_return_followers(self) -> None:
        Follow.objects.create(
            follower=self.second_user,
            following=self.user,
        )

        self.authenticate()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.data,
            [],
        )

    def test_following_returns_empty_list(self) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data,
            [],
        )

    def test_can_view_another_profiles_following(self) -> None:
        Follow.objects.create(
            follower=self.second_user,
            following=self.third_user,
        )

        self.authenticate()

        url = reverse(
            "user:profile-following",
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
            response.data[0]["nickname"],
            "kate",
        )

    def test_following_requires_authentication(self) -> None:
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class FollowersProfilesViewTests(BaseUserAPITestCase):
    def setUp(self) -> None:
        self.url = reverse(
            "user:profile-followers",
            args=[self.profile.pk],
        )

    def test_followers_returns_users_following_profile(self) -> None:
        Follow.objects.create(
            follower=self.second_user,
            following=self.user,
        )
        Follow.objects.create(
            follower=self.third_user,
            following=self.user,
        )

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
            for item in response.data
        }

        self.assertEqual(
            nicknames,
            {
                "bob",
                "kate",
            },
        )

    def test_followers_does_not_return_following(self) -> None:
        Follow.objects.create(
            follower=self.user,
            following=self.second_user,
        )

        self.authenticate()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.data,
            [],
        )

    def test_followers_returns_empty_list(self) -> None:
        self.authenticate()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            response.data,
            [],
        )

    def test_can_view_another_profiles_followers(self) -> None:
        Follow.objects.create(
            follower=self.third_user,
            following=self.second_user,
        )

        self.authenticate()

        url = reverse(
            "user:profile-followers",
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
            response.data[0]["nickname"],
            "kate",
        )

    def test_followers_requires_authentication(self) -> None:
        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class FollowDirectionTests(BaseUserAPITestCase):
    def test_followers_and_following_have_correct_direction(self) -> None:
        # Anna follows Bob.
        Follow.objects.create(
            follower=self.user,
            following=self.second_user,
        )

        # Kate follows Anna.
        Follow.objects.create(
            follower=self.third_user,
            following=self.user,
        )

        self.authenticate()

        following_response = self.client.get(
            reverse(
                "user:profile-following",
                args=[self.profile.pk],
            )
        )

        followers_response = self.client.get(
            reverse(
                "user:profile-followers",
                args=[self.profile.pk],
            )
        )

        self.assertEqual(
            following_response.status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            followers_response.status_code,
            status.HTTP_200_OK,
        )

        self.assertEqual(
            following_response.data[0]["nickname"],
            "bob",
        )

        self.assertEqual(
            followers_response.data[0]["nickname"],
            "kate",
        )
