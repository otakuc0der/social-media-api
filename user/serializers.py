from django.contrib.auth import authenticate
from django.db import transaction
from rest_framework import serializers

from user.models import Follow, Profile
from user.utils.validators import validate_unique_email


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        trim_whitespace=False,
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            raise serializers.ValidationError(
                "Unable to authenticate with provided credentials."
            )

        attrs["user"] = user
        return attrs


class ProfileCreateSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
    )
    password = serializers.CharField(
        source="user.password",
        write_only=True,
        trim_whitespace=False,
    )
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "nickname",
            "bio",
            "avatar",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value: str) -> str:
        return validate_unique_email(
            email=value,
            error_factory=serializers.ValidationError,
        )

    @transaction.atomic
    def create(self, validated_data):
        user_data = validated_data.pop("user")

        password = user_data.pop("password")

        user = Profile._meta.get_field("user").remote_field.model.objects.create_user(
            password=password,
            **user_data,
        )

        return Profile.objects.create(
            user=user,
            **validated_data,
        )


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
    )
    password = serializers.CharField(
        source="user.password",
        write_only=True,
        required=False,
        trim_whitespace=False,
    )
    first_name = serializers.CharField(
        source="user.first_name",
        required=False,
        allow_blank=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        required=False,
        allow_blank=True,
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "email",
            "password",
            "first_name",
            "last_name",
            "nickname",
            "bio",
            "avatar",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value: str) -> str:
        current_user_id = None

        if self.instance is not None:
            current_user_id = self.instance.user_id

        return validate_unique_email(
            email=value,
            error_factory=serializers.ValidationError,
            current_user_id=current_user_id,
        )

    @transaction.atomic
    def update(self, instance, validated_data):
        user_data = validated_data.pop(
            "user",
            {},
        )

        user = instance.user

        password = user_data.pop(
            "password",
            None,
        )

        for attribute, value in user_data.items():
            setattr(
                user,
                attribute,
                value,
            )

        if password:
            user.set_password(password)

        user.save()

        return super().update(
            instance,
            validated_data,
        )


class ProfileListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = [
            "id",
            "nickname",
            "avatar",
        ]


class ProfileDetailSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(
        source="user.first_name",
        read_only=True,
    )
    last_name = serializers.CharField(
        source="user.last_name",
        read_only=True,
    )

    class Meta:
        model = Profile
        fields = [
            "id",
            "nickname",
            "first_name",
            "last_name",
            "bio",
            "avatar",
        ]


class FollowSerializer(serializers.ModelSerializer):
    follower = serializers.CharField(
        source="follower.profile.nickname",
        read_only=True,
    )
    following = serializers.CharField(
        source="following.profile.nickname",
        read_only=True,
    )

    class Meta:
        model = Follow
        fields = [
            "id",
            "follower",
            "following",
        ]


class UnfollowSerializer(serializers.Serializer):
    pass


class FollowingProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source="following.profile.id",
        read_only=True,
    )
    nickname = serializers.CharField(
        source="following.profile.nickname",
        read_only=True,
    )
    avatar = serializers.ImageField(
        source="following.profile.avatar",
        read_only=True,
    )

    class Meta:
        model = Follow
        fields = [
            "id",
            "nickname",
            "avatar",
        ]


class FollowerProfileSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(
        source="follower.profile.id",
        read_only=True,
    )
    nickname = serializers.CharField(
        source="follower.profile.nickname",
        read_only=True,
    )
    avatar = serializers.ImageField(
        source="follower.profile.avatar",
        read_only=True,
    )

    class Meta:
        model = Follow
        fields = [
            "id",
            "nickname",
            "avatar",
        ]
