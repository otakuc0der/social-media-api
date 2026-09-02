from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from social.models import Post
from social.tasks import publish_post
from user.models import Profile


class PublishPostTaskTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="someone@example.com",
            password="password123",
        )

        Profile.objects.create(
            user=self.user,
            nickname="someone",
        )

    def create_post(
        self,
        *,
        status_value=Post.Status.SCHEDULED,
        scheduled_at=None,
        published_at=None,
    ) -> Post:
        return Post.objects.create(
            author=self.user,
            content="Some content is here!",
            status=status_value,
            scheduled_at=scheduled_at,
            published_at=published_at,
        )

    def test_publish_post_publishes_scheduled_post_when_time_has_arrived(
        self,
    ) -> None:
        post = self.create_post(
            scheduled_at=(timezone.now() - timedelta(minutes=1)),
        )

        publish_post(
            str(post.pk),
        )

        post.refresh_from_db()

        self.assertEqual(
            post.status,
            Post.Status.PUBLISHED,
        )

        self.assertIsNotNone(
            post.published_at,
        )

    def test_publish_post_does_not_publish_before_scheduled_time(
        self,
    ) -> None:
        post = self.create_post(
            scheduled_at=(timezone.now() + timedelta(hours=1)),
        )

        publish_post(
            str(post.pk),
        )

        post.refresh_from_db()

        self.assertEqual(
            post.status,
            Post.Status.SCHEDULED,
        )

        self.assertIsNone(
            post.published_at,
        )

    def test_publish_post_handles_deleted_post(
        self,
    ) -> None:
        post = self.create_post(
            scheduled_at=(timezone.now() + timedelta(hours=1)),
        )

        post_pk = post.pk
        post.delete()

        publish_post(
            str(post_pk),
        )

        self.assertFalse(
            Post.objects.filter(
                pk=post_pk,
            ).exists()
        )

    def test_publish_post_does_not_republish_already_published_post(
        self,
    ) -> None:
        published_at = timezone.now() - timedelta(hours=1)

        post = self.create_post(
            status_value=Post.Status.PUBLISHED,
            scheduled_at=(timezone.now() - timedelta(minutes=1)),
            published_at=published_at,
        )

        publish_post(
            str(post.pk),
        )

        post.refresh_from_db()

        self.assertEqual(
            post.status,
            Post.Status.PUBLISHED,
        )

        self.assertEqual(
            post.published_at,
            published_at,
        )
