from collections.abc import Callable
from uuid import UUID


ValidationErrorFactory = Callable[
    [dict[str, list[str]]],
    Exception,
]


def validate_like_creation(
    user_id: int,
    post_id: UUID,
    error_factory: ValidationErrorFactory,
) -> None:
    from social.models import Like

    if Like.objects.filter(
        user_id=user_id,
        post_id=post_id,
    ).exists():
        raise error_factory(
            {
                "like": [
                    "You have already liked this post."
                ],
            }
        )


def validate_like_removal(
    user_id: int,
    post_id: UUID,
    error_factory: ValidationErrorFactory,
) -> None:
    from social.models import Like

    if not Like.objects.filter(
        user_id=user_id,
        post_id=post_id,
    ).exists():
        raise error_factory(
            {
                "like": [
                    "You cannot remove a like from a post "
                    "you have not liked."
                ],
            }
        )
