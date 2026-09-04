from django.urls import reverse
from rest_framework import status

from social.models import Hashtag, Like
from social.tests.base import BaseSocialAPITestCase


class LikePostAPITests(BaseSocialAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.post = self.create_post(
            author=self.user,
        )

        self.like_url = reverse(
            "social:post-add-like",
            args=[self.post.pk],
        )

        self.unlike_url = reverse(
            "social:post-remove-like",
            args=[self.post.pk],
        )

    def test_like_post_creates_like(
        self,
    ) -> None:
        self.authenticate()

        response = self.client.post(
            self.like_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        self.assertTrue(
            Like.objects.filter(
                user=self.user,
                post=self.post,
            ).exists()
        )

    def test_cannot_like_same_post_twice(
        self,
    ) -> None:
        Like.objects.create(
            user=self.user,
            post=self.post,
        )

        self.authenticate()

        response = self.client.post(
            self.like_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertEqual(
            Like.objects.filter(
                user=self.user,
                post=self.post,
            ).count(),
            1,
        )

    def test_unlike_post_deletes_like(
        self,
    ) -> None:
        Like.objects.create(
            user=self.user,
            post=self.post,
        )

        self.authenticate()

        response = self.client.post(
            self.unlike_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_204_NO_CONTENT,
        )

        self.assertFalse(
            Like.objects.filter(
                user=self.user,
                post=self.post,
            ).exists()
        )

    def test_cannot_unlike_post_not_liked(
        self,
    ) -> None:
        self.authenticate()

        response = self.client.post(
            self.unlike_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_like_requires_authentication(
        self,
    ) -> None:
        response = self.client.post(
            self.like_url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


class LikedPostsAPITests(BaseSocialAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.url = reverse(
            "social:post-liked-posts",
        )

    def test_liked_posts_returns_only_current_users_likes(
        self,
    ) -> None:
        liked_post = self.create_post(
            author=self.user,
            content="Liked.",
        )

        not_liked_post = self.create_post(
            author=self.user,
            content="Not liked.",
        )

        Like.objects.create(
            user=self.user,
            post=liked_post,
        )

        self.authenticate()

        response = self.client.get(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertIn(
            str(liked_post.pk),
            post_ids,
        )

        self.assertNotIn(
            str(not_liked_post.pk),
            post_ids,
        )

    def test_liked_posts_applies_post_filters(
        self,
    ) -> None:
        python_hashtag = Hashtag.objects.create(
            name="python",
        )

        travel_hashtag = Hashtag.objects.create(
            name="travel",
        )

        python_post = self.create_post(
            author=self.user,
            content="Python.",
        )

        travel_post = self.create_post(
            author=self.user,
            content="Travel.",
        )

        python_post.hashtags.add(
            python_hashtag,
        )

        travel_post.hashtags.add(
            travel_hashtag,
        )

        Like.objects.create(
            user=self.user,
            post=python_post,
        )

        Like.objects.create(
            user=self.user,
            post=travel_post,
        )

        self.authenticate()

        response = self.client.get(
            self.url,
            {
                "hashtags_names": "python",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertIn(
            str(python_post.pk),
            post_ids,
        )

        self.assertNotIn(
            str(travel_post.pk),
            post_ids,
        )
