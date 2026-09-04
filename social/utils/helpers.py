from typing import TYPE_CHECKING

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import AnonymousUser
from django.db.models import Q, QuerySet

if TYPE_CHECKING:
    from social.models import Post


def get_available_posts_for_user(
    user: AbstractBaseUser | AnonymousUser,
    queryset: QuerySet["Post"],
) -> QuerySet["Post"]:
    from social.models import Post

    return queryset.filter(
        Q(author=user)
        | Q(
            author__follower_relations__follower=user,
            status=Post.Status.PUBLISHED,
        )
    ).distinct()
