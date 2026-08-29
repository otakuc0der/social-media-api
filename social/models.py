import uuid
from typing import Any

from django.conf import settings
from django.db import models
from django.db.models import UniqueConstraint
from django.core.exceptions import ValidationError

from social.utils.validators import validate_follower_following
from social_media_api.utils.files import generate_image_file_path


class Follow(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="following_relations",
    )
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="follower_relations",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(
                fields=["follower", "following"], name="unique_follower_following"
            )
        ]

    def clean(self) -> None:
        super().clean()
        validate_follower_following(
            self.follower,
            self.following,
            ValidationError,
        )

    def save(
        self,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return (
            f"{self.follower.profile.nickname} "
            f"follows {self.following.profile.nickname}"
        )


class Hashtag(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(unique=True, max_length=255)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


def post_image_file_path(
    post: "Post",
    filename: str,
) -> str:
    return generate_image_file_path(
        str(post.id),
        filename,
        "uploads/posts",
    )


class Post(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled"
        PUBLISHED = "published"

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    content = models.TextField()
    image = models.ImageField(null=True, blank=True, upload_to=post_image_file_path)
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PUBLISHED
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    hashtags = models.ManyToManyField(
        Hashtag,
        related_name="posts",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Post {self.id}, created at {self.created_at}"


class Like(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="likes"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_post_like",
            )
        ]

    def __str__(self) -> str:
        return f"{self.user.profile.nickname} likes {self.post}"


class Comment(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.author.profile.nickname} comments {self.post}"
