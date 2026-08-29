from typing import Any

from django.contrib.auth import authenticate, get_user_model
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from user.models import Profile
from user.utils.validators import validate_unique_email


class CustomAuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_("Email"),
        write_only=True,
    )
    password = serializers.CharField(
        label=_("Password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True,
    )

    def validate(
        self,
        attrs: dict[str, Any],
    ) -> dict[str, Any]:
        email = attrs.get("email")
        password = attrs.get("password")

        if not email or not password:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(
                msg,
                code="authorization",
            )

        user = authenticate(
            request=self.context.get("request"),
            email=email,
            password=password,
        )

        if not user:
            msg = _("Unable to log in with provided credentials.")
            raise serializers.ValidationError(
                msg,
                code="authorization",
            )

        attrs["user"] = user

        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        source="user.email",
        allow_blank=False,
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
    password = serializers.CharField(
        source="user.password",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=False,
        allow_blank=False,
    )
    avatar = serializers.ImageField(
        required=False,
        allow_empty_file=False,
        allow_null=True,
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
            "email",
            "password",
        ]
        read_only_fields = ["id"]

    def validate_email(self, value: str) -> str:
        current_user_id = None

        if self.instance:
            current_user_id = self.instance.user_id

        return validate_unique_email(
            email=value,
            error_to_raise=serializers.ValidationError,
            current_user_id=current_user_id,
        )

    def update(
        self,
        instance: Profile,
        validated_data: dict[str, Any],
    ) -> Profile:
        with transaction.atomic():
            user_data = validated_data.pop("user", {})
            user = instance.user

            password = user_data.pop("password", None)

            for field, value in user_data.items():
                setattr(user, field, value)

            if password:
                user.set_password(password)

            if user_data or password:
                user.save()

            for field, value in validated_data.items():
                setattr(instance, field, value)

            instance.save()

        return instance


class ProfileCreateSerializer(ProfileSerializer):
    password = serializers.CharField(
        source="user.password",
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
        required=True,
        allow_blank=False,
    )

    def create(
        self,
        validated_data: dict[str, Any],
    ) -> Profile:
        user_data = validated_data.pop("user")
        password = user_data.pop("password")

        with transaction.atomic():
            user = get_user_model().objects.create_user(
                password=password,
                **user_data,
            )

            profile = Profile.objects.create(
                user=user,
                **validated_data,
            )

        return profile


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
        read_only_fields = fields
