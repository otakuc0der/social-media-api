import uuid
from typing import Any

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext as _

from social_media_api.utils.files import generate_image_file_path
from user.managers import UserManager
from user.utils.validators import validate_follow_creation


class User(AbstractUser):
    username = None
    email = models.EmailField(
        _("email address"),
        unique=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self) -> str:
        return self.email


def profile_image_file_path(
    profile: "Profile",
    filename: str,
) -> str:
    return generate_image_file_path(
        str(profile.id),
        filename,
        "uploads/profiles",
    )


class Profile(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    nickname = models.CharField(unique=True, max_length=100)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_image_file_path)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nickname"]

    def __str__(self) -> str:
        return self.nickname


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
                fields=["follower", "following"],
                name="unique_follower_following",
            )
        ]

    def clean(self) -> None:
        super().clean()

        validate_follow_creation(
            follower_id=self.follower_id,
            following_id=self.following_id,
            error_factory=ValidationError,
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
