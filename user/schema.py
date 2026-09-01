from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
)
from rest_framework import serializers

from user.serializers import (
    CustomAuthTokenSerializer,
    FollowerProfileSerializer,
    FollowingProfileSerializer,
    FollowSerializer,
    ProfileCreateSerializer,
    ProfileDetailSerializer,
    ProfileListSerializer,
    ProfileSerializer,
)

REGISTER_SCHEMA = extend_schema(
    summary="Register user",
    description=(
        "Create a new user account together with its profile. "
        "Email and nickname must be unique."
    ),
    request=ProfileCreateSerializer,
    responses={
        201: ProfileCreateSerializer,
        400: OpenApiResponse(
            description="Invalid registration data.",
            examples=[
                OpenApiExample(
                    "Email already exists",
                    value={
                        "email": ["A user with this email already exists."],
                    },
                ),
                OpenApiExample(
                    "Nickname already exists",
                    value={
                        "nickname": ["Profile with this nickname already exists."],
                    },
                ),
            ],
        ),
    },
    examples=[
        OpenApiExample(
            "Registration request",
            value={
                "email": "daniel@example.com",
                "password": "strong-password",
                "nickname": "daniel_codes",
                "first_name": "Daniel",
                "last_name": "Lee",
                "bio": "Backend developer and Python enthusiast.",
            },
            request_only=True,
        ),
    ],
    tags=["Authentication"],
)


LOGIN_SCHEMA = extend_schema(
    summary="Log in",
    description=(
        "Authenticate a user with email and password and return an "
        "authentication token. Use the returned token in subsequent "
        "requests as: Authorization: Token <token>."
    ),
    request=CustomAuthTokenSerializer,
    responses={
        200: serializers.DictField(
            child=serializers.CharField(),
        ),
        400: OpenApiResponse(
            description="Invalid credentials or invalid request data.",
            examples=[
                OpenApiExample(
                    "Invalid credentials",
                    value={
                        "non_field_errors": [
                            "Unable to log in with provided credentials."
                        ],
                    },
                ),
            ],
        ),
    },
    examples=[
        OpenApiExample(
            "Login request",
            value={
                "email": "daniel@example.com",
                "password": "strong-password",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Login response",
            value={
                "token": ("0123456789abcdef" "0123456789abcdef" "01234567"),
            },
            response_only=True,
            status_codes=["200"],
        ),
    ],
    tags=["Authentication"],
)


LOGOUT_SCHEMA = extend_schema(
    summary="Log out",
    description=(
        "Log out the authenticated user by deleting their current "
        "authentication token. The deleted token can no longer be used."
    ),
    request=None,
    responses={
        200: OpenApiResponse(
            description="Logged out successfully.",
            examples=[
                OpenApiExample(
                    "Successful logout",
                    value={
                        "message": "Logged out successfully",
                    },
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided or are invalid.",
        ),
    },
    tags=["Authentication"],
)


CURRENT_PROFILE_RETRIEVE_SCHEMA = extend_schema(
    summary="Retrieve current profile",
    description=(
        "Return the profile and account information belonging to the "
        "currently authenticated user."
    ),
    responses={
        200: ProfileSerializer,
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    tags=["Current profile"],
)


CURRENT_PROFILE_UPDATE_SCHEMA = extend_schema(
    summary="Update current profile",
    description=(
        "Replace editable profile and account information belonging to "
        "the currently authenticated user."
    ),
    request=ProfileSerializer,
    responses={
        200: ProfileSerializer,
        400: OpenApiResponse(
            description="Invalid profile data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    tags=["Current profile"],
)


CURRENT_PROFILE_PARTIAL_UPDATE_SCHEMA = extend_schema(
    summary="Partially update current profile",
    description=(
        "Update one or more editable fields belonging to the currently "
        "authenticated user's account or profile."
    ),
    request=ProfileSerializer,
    responses={
        200: ProfileSerializer,
        400: OpenApiResponse(
            description="Invalid profile data.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    examples=[
        OpenApiExample(
            "Update bio",
            value={
                "bio": "Updated profile bio.",
            },
            request_only=True,
        ),
        OpenApiExample(
            "Update nickname",
            value={
                "nickname": "new_nickname",
            },
            request_only=True,
        ),
    ],
    tags=["Current profile"],
)


CURRENT_PROFILE_DELETE_SCHEMA = extend_schema(
    summary="Delete current account",
    description=(
        "Permanently delete the authenticated user account. "
        "The associated profile and related objects are deleted according "
        "to configured cascade relationships."
    ),
    request=None,
    responses={
        204: OpenApiResponse(
            description="Account deleted successfully.",
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    tags=["Current profile"],
)


PROFILE_LIST_SCHEMA = extend_schema(
    summary="List profiles",
    description=(
        "Return a paginated list of user profiles. "
        "Profiles can be searched by nickname, email, first name, "
        "and last name."
    ),
    parameters=[
        OpenApiParameter(
            name="nickname",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=("Filter by nickname using a case-insensitive partial match."),
        ),
        OpenApiParameter(
            name="email",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=("Filter by email using a case-insensitive partial match."),
        ),
        OpenApiParameter(
            name="first_name",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=(
                "Filter by first name using a case-insensitive partial match."
            ),
        ),
        OpenApiParameter(
            name="last_name",
            type=str,
            location=OpenApiParameter.QUERY,
            required=False,
            description=("Filter by last name using a case-insensitive partial match."),
        ),
    ],
    responses={
        200: ProfileListSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
    },
    tags=["Profiles"],
)


PROFILE_RETRIEVE_SCHEMA = extend_schema(
    summary="Retrieve profile",
    description=("Return detailed information about the selected user profile."),
    responses={
        200: ProfileDetailSerializer,
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Profile not found.",
        ),
    },
    tags=["Profiles"],
)


FOLLOW_PROFILE_SCHEMA = extend_schema(
    summary="Follow profile",
    description=(
        "Follow the user associated with the selected profile. "
        "A user cannot follow themselves and cannot create the same "
        "follow relationship more than once."
    ),
    request=None,
    responses={
        201: FollowSerializer,
        400: OpenApiResponse(
            description="Invalid follow operation.",
            examples=[
                OpenApiExample(
                    "Self follow",
                    value={
                        "follower": ["You can't follow yourself."],
                    },
                ),
                OpenApiExample(
                    "Already following",
                    value={
                        "following": ["You already follow this profile."],
                    },
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Profile not found.",
        ),
    },
    tags=["Follows"],
)


UNFOLLOW_PROFILE_SCHEMA = extend_schema(
    summary="Unfollow profile",
    description=(
        "Remove the follow relationship between the authenticated user "
        "and the user associated with the selected profile."
    ),
    request=None,
    responses={
        204: OpenApiResponse(
            description="Profile unfollowed successfully.",
        ),
        400: OpenApiResponse(
            description="Invalid unfollow operation.",
            examples=[
                OpenApiExample(
                    "Self unfollow",
                    value={
                        "follower": ["You can't unfollow yourself."],
                    },
                ),
                OpenApiExample(
                    "Relationship does not exist",
                    value={
                        "following": ["You don't follow this profile."],
                    },
                ),
            ],
        ),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Profile not found.",
        ),
    },
    tags=["Follows"],
)


FOLLOWING_LIST_SCHEMA = extend_schema(
    summary="List following",
    description=(
        "Return a paginated list of users followed by the user associated "
        "with the selected profile."
    ),
    responses={
        200: FollowingProfileSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Profile not found.",
        ),
    },
    tags=["Follows"],
)


FOLLOWERS_LIST_SCHEMA = extend_schema(
    summary="List followers",
    description=(
        "Return a paginated list of users who follow the user associated "
        "with the selected profile."
    ),
    responses={
        200: FollowerProfileSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication required.",
        ),
        404: OpenApiResponse(
            description="Profile not found.",
        ),
    },
    tags=["Follows"],
)
