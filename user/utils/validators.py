from typing import Callable

from django.contrib.auth import get_user_model


FieldValidationErrorType = Callable[
    [list[str]],
    Exception,
]


def validate_unique_email(
    email: str,
    error_to_raise: FieldValidationErrorType,
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
        raise error_to_raise(
            [
                "A user with this email already exists.",
            ]
        )

    return user_model.objects.normalize_email(email)
