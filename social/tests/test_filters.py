from datetime import timedelta

from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from social.models import Comment, Hashtag, Post
from social.tests.base import BaseSocialAPITestCase


class PostFilterTests(BaseSocialAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.url = reverse(
            "social:post-list",
        )

        self.follow()

        self.python = Hashtag.objects.create(
            name="python",
        )
        self.django = Hashtag.objects.create(
            name="django",
        )
        self.travel = Hashtag.objects.create(
            name="travel",
        )

        self.own_post = self.create_post(
            author=self.user,
            content="Own post.",
        )

        self.followed_post = self.create_post(
            author=self.second_user,
            content="Followed post.",
        )

        self.unavailable_post = self.create_post(
            author=self.third_user,
            content="Unavailable post.",
        )

        self.authenticate()

    def test_filter_by_own_author(
        self,
    ) -> None:
        response = self.client.get(
            self.url,
            {
                "author": self.user.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertEqual(
            post_ids,
            {
                str(self.own_post.pk),
            },
        )

    def test_filter_by_followed_author(
        self,
    ) -> None:
        response = self.client.get(
            self.url,
            {
                "author": self.second_user.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertEqual(
            post_ids,
            {
                str(self.followed_post.pk),
            },
        )

    def test_filter_rejects_unavailable_author(
        self,
    ) -> None:
        response = self.client.get(
            self.url,
            {
                "author": self.third_user.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_filter_by_hashtag_ids(
        self,
    ) -> None:
        self.own_post.hashtags.add(
            self.python,
        )

        self.followed_post.hashtags.add(
            self.travel,
        )

        response = self.client.get(
            self.url,
            {
                "hashtags": str(self.python.pk),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertEqual(
            post_ids,
            {
                str(self.own_post.pk),
            },
        )

    def test_filter_hashtag_names_matches_any_hashtag(
        self,
    ) -> None:
        self.own_post.hashtags.add(
            self.python,
        )

        self.followed_post.hashtags.add(
            self.travel,
        )

        response = self.client.get(
            self.url,
            {
                "hashtags_names": "python,travel",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertEqual(
            post_ids,
            {
                str(self.own_post.pk),
                str(self.followed_post.pk),
            },
        )

    def test_filter_hashtags_all_names_requires_all_hashtags(
        self,
    ) -> None:
        self.own_post.hashtags.add(
            self.python,
            self.django,
        )

        self.followed_post.hashtags.add(
            self.python,
        )

        response = self.client.get(
            self.url,
            {
                "hashtags_all_names": "python,django",
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertEqual(
            post_ids,
            {
                str(self.own_post.pk),
            },
        )

    def test_filter_hashtags_all_names_is_case_insensitive(
        self,
    ) -> None:
        self.own_post.hashtags.add(
            self.python,
            self.django,
        )

        response = self.client.get(
            self.url,
            {
                "hashtags_all_names": "PYTHON,DJANGO",
            },
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertEqual(
            post_ids,
            {
                str(self.own_post.pk),
            },
        )

    def test_filter_by_created_at_range(
        self,
    ) -> None:
        now = timezone.now()

        old_post = self.create_post(
            author=self.user,
            content="Old post.",
        )

        recent_post = self.create_post(
            author=self.user,
            content="Recent post.",
        )

        Post.objects.filter(
            pk=old_post.pk,
        ).update(
            created_at=(now - timedelta(days=10)),
        )

        Post.objects.filter(
            pk=recent_post.pk,
        ).update(
            created_at=now,
        )

        response = self.client.get(
            self.url,
            {
                "created_at_after": (now.date() - timedelta(days=1)).isoformat(),
                "created_at_before": (now.date() + timedelta(days=1)).isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertIn(
            str(recent_post.pk),
            post_ids,
        )

        self.assertNotIn(
            str(old_post.pk),
            post_ids,
        )

    def test_filter_by_published_at_range(
        self,
    ) -> None:
        now = timezone.now()

        old_post = self.create_post(
            author=self.user,
            content="Old published.",
            published_at=(now - timedelta(days=10)),
        )

        recent_post = self.create_post(
            author=self.user,
            content="Recent published.",
            published_at=now,
        )

        response = self.client.get(
            self.url,
            {
                "published_at_after": (now.date() - timedelta(days=1)).isoformat(),
                "published_at_before": (now.date() + timedelta(days=1)).isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        post_ids = {item["id"] for item in self.get_results(response)}

        self.assertIn(
            str(recent_post.pk),
            post_ids,
        )

        self.assertNotIn(
            str(old_post.pk),
            post_ids,
        )


class CommentFilterTests(BaseSocialAPITestCase):
    def setUp(self) -> None:
        super().setUp()

        self.post = self.create_post(
            author=self.user,
        )

        self.user_comment = Comment.objects.create(
            author=self.user,
            post=self.post,
            content="Anna comment.",
        )

        self.second_comment = Comment.objects.create(
            author=self.second_user,
            post=self.post,
            content="Bob comment.",
        )

        self.url = reverse(
            "social:comment-list",
            kwargs={
                "post_pk": self.post.pk,
            },
        )

        self.authenticate()

    def test_filter_comments_by_author(
        self,
    ) -> None:
        response = self.client.get(
            self.url,
            {
                "author": self.second_user.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        comments = self.get_results(
            response,
        )

        self.assertEqual(
            len(comments),
            1,
        )

        self.assertEqual(
            comments[0]["id"],
            str(self.second_comment.pk),
        )

    def test_author_filter_contains_only_authors_from_current_post(
        self,
    ) -> None:
        another_post = self.create_post(
            author=self.user,
        )

        Comment.objects.create(
            author=self.third_user,
            post=another_post,
            content="Kate comment.",
        )

        response = self.client.get(
            self.url,
            {
                "author": self.third_user.pk,
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST,
        )

    def test_filter_comments_by_created_at_range(
        self,
    ) -> None:
        now = timezone.now()

        Comment.objects.filter(
            pk=self.user_comment.pk,
        ).update(
            created_at=(now - timedelta(days=10)),
        )

        Comment.objects.filter(
            pk=self.second_comment.pk,
        ).update(
            created_at=now,
        )

        response = self.client.get(
            self.url,
            {
                "created_at_after": (now.date() - timedelta(days=1)).isoformat(),
                "created_at_before": (now.date() + timedelta(days=1)).isoformat(),
            },
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK,
        )

        comment_ids = {item["id"] for item in self.get_results(response)}

        self.assertIn(
            str(self.second_comment.pk),
            comment_ids,
        )

        self.assertNotIn(
            str(self.user_comment.pk),
            comment_ids,
        )
