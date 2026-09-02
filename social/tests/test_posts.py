from datetime import timedelta
from unittest.mock import patch

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from social.models import Post
from social.tests.base import BaseSocialAPITestCase

POST_URL = reverse(
    "social:post-list",
)

PUBLISH_POST_TASK_PATH = "social.views.publish_post.apply_async"


class PostVisibilityAPITests(BaseSocialAPITestCase):
    def test_post_list_includes_own_posts(
        self,
    ) -> None:
        post = self.create_post(
            author=self.user,
        )

        self.authenticate()

        response = self.client.get(
            POST_URL,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertIn(
            str(post.pk),
            post_ids,
        )

    def test_post_list_includes_published_posts_from_followed_users(
        self,
    ) -> None:
        self.follow()

        post = self.create_post(
            author=self.second_user,
        )

        self.authenticate()

        response = self.client.get(
            POST_URL,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertIn(
            str(post.pk),
            post_ids,
        )

    def test_post_list_excludes_posts_from_unfollowed_users(
        self,
    ) -> None:
        post = self.create_post(
            author=self.second_user,
        )

        self.authenticate()

        response = self.client.get(
            POST_URL,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertNotIn(
            str(post.pk),
            post_ids,
        )

    def test_post_list_excludes_scheduled_posts_from_followed_users(
        self,
    ) -> None:
        self.follow()

        post = self.create_post(
            author=self.second_user,
            status_value=Post.Status.SCHEDULED,
            scheduled_at=(timezone.now() + timedelta(hours=1)),
            published_at=None,
        )

        self.authenticate()

        response = self.client.get(
            POST_URL,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertNotIn(
            str(post.pk),
            post_ids,
        )

    def test_post_list_includes_own_scheduled_posts(
        self,
    ) -> None:
        post = self.create_post(
            author=self.user,
            status_value=Post.Status.SCHEDULED,
            scheduled_at=(timezone.now() + timedelta(hours=1)),
            published_at=None,
        )

        self.authenticate()

        response = self.client.get(
            POST_URL,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertIn(
            str(post.pk),
            post_ids,
        )


class PostPermissionsAPITests(BaseSocialAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.follow()

        self.post = self.create_post(
            author=self.second_user,
            content="Original content.",
        )

        self.url = reverse(
            "social:post-detail",
            args=[self.post.pk],
        )

    def test_user_cannot_update_another_users_post(
        self,
    ) -> None:
        self.authenticate()

        response = self.client.patch(
            self.url,
            {
                "content": "Changed content.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.post.refresh_from_db()

        self.assertEqual(
            self.post.content,
            "Original content.",
        )

    def test_user_cannot_delete_another_users_post(
        self,
    ) -> None:
        self.authenticate()

        response = self.client.delete(
            self.url,
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Post.objects.filter(
                pk=self.post.pk,
            ).exists()
        )


class PostSchedulingAPITests(BaseSocialAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.authenticate()

    def get_post_detail_url(
        self,
        post_pk,
    ) -> str:
        return reverse(
            "social:post-detail",
            args=[post_pk],
        )

    @patch(PUBLISH_POST_TASK_PATH)
    def test_create_post_without_scheduled_at_publishes_immediately(
        self,
        mock_apply_async,
    ) -> None:
        response = self.client.post(
            path=POST_URL,
            data={
                "content": "Some post info.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        post = Post.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            post.status,
            Post.Status.PUBLISHED,
        )
        self.assertIsNone(
            post.scheduled_at,
        )
        self.assertIsNotNone(
            post.published_at,
        )

        mock_apply_async.assert_not_called()

    @patch(PUBLISH_POST_TASK_PATH)
    def test_create_scheduled_post_schedules_publish_task(
        self,
        mock_apply_async,
    ) -> None:
        scheduled_at = timezone.now() + timedelta(hours=1)

        with self.captureOnCommitCallbacks(
            execute=True,
        ) as callbacks:
            response = self.client.post(
                path=POST_URL,
                data={
                    "content": "Some post info.",
                    "scheduled_at": scheduled_at,
                },
                format="json",
            )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        post = Post.objects.get(
            pk=response.data["id"],
        )

        self.assertEqual(
            post.status,
            Post.Status.SCHEDULED,
        )
        self.assertEqual(
            post.scheduled_at,
            scheduled_at,
        )
        self.assertIsNone(
            post.published_at,
        )

        self.assertEqual(
            len(callbacks),
            1,
        )

        mock_apply_async.assert_called_once_with(
            args=[str(post.pk)],
            eta=scheduled_at,
        )

    @patch(PUBLISH_POST_TASK_PATH)
    def test_create_post_with_past_scheduled_at_is_rejected(
        self,
        mock_apply_async,
    ) -> None:
        response = self.client.post(
            path=POST_URL,
            data={
                "content": "Some post info.",
                "scheduled_at": (timezone.now() - timedelta(hours=1)),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "scheduled_at",
            response.data,
        )

        self.assertFalse(
            Post.objects.exists(),
        )

        mock_apply_async.assert_not_called()

    @patch(PUBLISH_POST_TASK_PATH)
    def test_update_post_scheduled_at_is_rejected(
        self,
        mock_apply_async,
    ) -> None:
        scheduled_at = timezone.now() + timedelta(hours=1)

        with self.captureOnCommitCallbacks(
            execute=True,
        ):
            response = self.client.post(
                path=POST_URL,
                data={
                    "content": "Some post info.",
                    "scheduled_at": scheduled_at,
                },
                format="json",
            )

        post = Post.objects.get(
            pk=response.data["id"],
        )

        response = self.client.patch(
            path=self.get_post_detail_url(
                post.pk,
            ),
            data={
                "scheduled_at": (scheduled_at + timedelta(hours=2)),
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

        self.assertIn(
            "scheduled_at",
            response.data,
        )

        post.refresh_from_db()

        self.assertEqual(
            post.scheduled_at,
            scheduled_at,
        )
