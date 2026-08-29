from typing import Callable

from django.contrib.auth import get_user_model


FieldValidationErrorFactory = Callable[
    [list[str]],
    Exception,
]

ValidationErrorFactory = Callable[
    [dict[str, list[str]]],
    Exception,
]


def validate_unique_email(
    email: str,
    error_factory: FieldValidationErrorFactory,
    current_user_id: int | None = None,
) -> str:
    user_model = get_user_model()

    queryset = user_model.objects.filter(
        email__iexact=email,
    )

    if current_user_id is not None:
        queryset = queryset.exclude(
            pk=current_user_id,
        )

    if queryset.exists():
        raise error_factory(
            [
                "A user with this email already exists.",
            ]
        )

    return user_model.objects.normalize_email(email)


def validate_follow_creation(
    follower_id: int,
    following_id: int,
    error_factory: ValidationErrorFactory,
) -> None:
    from user.models import Follow

    if follower_id == following_id:
        raise error_factory(
            {
                "follower": [
                    "You can't follow yourself.",
                ]
            }
        )

    if Follow.objects.filter(
        follower_id=follower_id,
        following_id=following_id,
    ).exists():
        raise error_factory(
            {
                "following": [
                    "You already follow this profile.",
                ]
            }
        )


def validate_unfollow(
    follower_id: int,
    following_id: int,
    error_factory: ValidationErrorFactory,
) -> None:
    from user.models import Follow

    if follower_id == following_id:
        raise error_factory(
            {
                "follower": [
                    "You can't unfollow yourself.",
                ]
            }
        )

    if not Follow.objects.filter(
        follower_id=follower_id,
        following_id=following_id,
    ).exists():
        raise error_factory(
            {
                "following": [
                    "You don't follow this profile.",
                ]
            }
        )
