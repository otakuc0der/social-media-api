from typing import Any, Callable


ValidationErrorType = Callable[
    [dict[str, list[str]]],
    Exception,
]


def validate_follower_following(
    follower: Any,
    following: Any,
    error_to_raise: ValidationErrorType,
) -> None:
    if follower == following:
        raise error_to_raise(
            {
                "follower": [
                    "You can't follow yourself."
                ]
            }
        )
