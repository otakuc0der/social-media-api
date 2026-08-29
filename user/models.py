import uuid

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _

from social_media_api.utils.files import generate_image_file_path
from user.managers import UserManager


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
