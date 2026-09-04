from django.urls import reverse
from rest_framework import status

from social.models import Comment
from social.tests.base import BaseSocialAPITestCase


class CommentAPITests(BaseSocialAPITestCase):
    def get_comment_list_url(
        self,
        post_pk,
    ) -> str:
        return reverse(
            "social:comment-list",
            kwargs={
                "post_pk": post_pk,
            },
        )

    def get_comment_detail_url(
        self,
        post_pk,
        comment_pk,
    ) -> str:
        return reverse(
            "social:comment-detail",
            kwargs={
                "post_pk": post_pk,
                "pk": comment_pk,
            },
        )

    def test_create_comment_on_own_post(
        self,
    ) -> None:
        post = self.create_post(
            author=self.user,
        )

        self.authenticate()

        response = self.client.post(
            self.get_comment_list_url(
                post.pk,
            ),
            {
                "content": "Great post!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                post=post,
                content="Great post!",
            ).exists()
        )

    def test_create_comment_on_followed_users_post(
        self,
    ) -> None:
        self.follow()

        post = self.create_post(
            author=self.second_user,
        )

        self.authenticate()

        response = self.client.post(
            self.get_comment_list_url(
                post.pk,
            ),
            {
                "content": "Nice!",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED,
        )

        self.assertTrue(
            Comment.objects.filter(
                author=self.user,
                post=post,
            ).exists()
        )

    def test_create_comment_on_unavailable_post_returns_404(
        self,
    ) -> None:
        post = self.create_post(
            author=self.second_user,
        )

        self.authenticate()

        response = self.client.post(
            self.get_comment_list_url(
                post.pk,
            ),
            {
                "content": "Should not work.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
        )

        self.assertFalse(
            Comment.objects.filter(
                author=self.user,
                post=post,
            ).exists()
        )

    def test_user_cannot_update_another_users_comment(
        self,
    ) -> None:
        post = self.create_post(
            author=self.user,
        )

        comment = Comment.objects.create(
            author=self.second_user,
            post=post,
            content="Original content.",
        )

        self.authenticate()

        response = self.client.patch(
            self.get_comment_detail_url(
                post.pk,
                comment.pk,
            ),
            {
                "content": "Changed content.",
            },
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        comment.refresh_from_db()

        self.assertEqual(
            comment.content,
            "Original content.",
        )

    def test_user_cannot_delete_another_users_comment(
        self,
    ) -> None:
        post = self.create_post(
            author=self.user,
        )

        comment = Comment.objects.create(
            author=self.second_user,
            post=post,
            content="Original content.",
        )

        self.authenticate()

        response = self.client.delete(
            self.get_comment_detail_url(
                post.pk,
                comment.pk,
            ),
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_403_FORBIDDEN,
        )

        self.assertTrue(
            Comment.objects.filter(
                pk=comment.pk,
            ).exists()
        )
