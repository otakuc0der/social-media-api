import json
import os
import random
from datetime import timedelta
from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from user.models import Profile


PROFILE_FIXTURE_PASSWORD = os.getenv(
    "PROFILE_FIXTURE_PASSWORD",
    "password123",
)


PROFILES = [
    {
        "email": "alex.johnson@example.com",
        "first_name": "Alex",
        "last_name": "Johnson",
        "nickname": "alex_travels",
        "bio": (
            "Travel enthusiast exploring new cities, local cultures, and "
            "hidden places. I share stories from my trips, practical travel "
            "tips, and destinations that are worth visiting."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "emma.wilson@example.com",
        "first_name": "Emma",
        "last_name": "Wilson",
        "nickname": "emma_reads",
        "bio": (
            "Book lover interested in contemporary fiction, classics, and "
            "non-fiction. I share reviews, reading notes, recommendations, "
            "and thoughts from my personal bookshelf."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "daniel.lee@example.com",
        "first_name": "Daniel",
        "last_name": "Lee",
        "nickname": "daniel_codes",
        "bio": (
            "Backend developer working with Python and Django. Interested in "
            "REST APIs, databases, testing, clean architecture, and learning "
            "better approaches to software development."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "sophia.martin@example.com",
        "first_name": "Sophia",
        "last_name": "Martin",
        "nickname": "sophia_cooks",
        "bio": (
            "Home cook who enjoys experimenting with simple recipes, fresh "
            "ingredients, and new combinations. I share everyday meals, "
            "baking experiments, and practical cooking ideas."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "michael.brown@example.com",
        "first_name": "Michael",
        "last_name": "Brown",
        "nickname": "mike_frames",
        "bio": (
            "Street photographer capturing architecture, people, and small "
            "moments from everyday city life. Always looking for interesting "
            "light, unusual details, and new perspectives."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "olivia.davis@example.com",
        "first_name": "Olivia",
        "last_name": "Davis",
        "nickname": "olivia_moves",
        "bio": (
            "Fitness enthusiast focused on strength training, running, and an "
            "active lifestyle. I share workouts, progress, motivation, and "
            "lessons learned along the way."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "ethan.clark@example.com",
        "first_name": "Ethan",
        "last_name": "Clark",
        "nickname": "ethan_music",
        "bio": (
            "Guitar player and music enthusiast who spends too much time "
            "building playlists. I share albums, live performances, and songs "
            "that deserve more attention."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "mia.anderson@example.com",
        "first_name": "Mia",
        "last_name": "Anderson",
        "nickname": "mia_creates",
        "bio": (
            "Digital artist interested in illustration, typography, and visual "
            "storytelling. I share sketches, finished work, experiments, and "
            "different parts of my creative process."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "noah.walker@example.com",
        "first_name": "Noah",
        "last_name": "Walker",
        "nickname": "noah_outdoors",
        "bio": (
            "Outdoor enthusiast who prefers weekends on hiking trails and in "
            "the mountains. I share routes, camping experiences, equipment "
            "notes, and photos from nature."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "ava.thomas@example.com",
        "first_name": "Ava",
        "last_name": "Thomas",
        "nickname": "ava_foodie",
        "bio": (
            "Always looking for interesting cafes, restaurants, and local "
            "dishes. I share food discoveries, honest impressions, and places "
            "I would happily visit again."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "liam.harris@example.com",
        "first_name": "Liam",
        "last_name": "Harris",
        "nickname": "liam_tech",
        "bio": (
            "Technology enthusiast interested in software, hardware, and new "
            "digital products. I enjoy testing tools, discussing trends, and "
            "sharing useful discoveries."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "isabella.moore@example.com",
        "first_name": "Isabella",
        "last_name": "Moore",
        "nickname": "bella_gardens",
        "bio": (
            "Plant lover learning more about gardening, indoor plants, and "
            "sustainable living. I share growing experiments, small victories, "
            "and lessons from keeping things green."
        ),
        "is_staff": False,
        "is_superuser": False,
    },
    {
        "email": "staff.one@example.com",
        "first_name": "Grace",
        "last_name": "Miller",
        "nickname": "grace_staff",
        "bio": (
            "Community moderator helping keep discussions useful, respectful, "
            "and organized. Interested in online communities and content "
            "management."
        ),
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "email": "staff.two@example.com",
        "first_name": "Henry",
        "last_name": "Wilson",
        "nickname": "henry_staff",
        "bio": (
            "Platform team member focused on moderation workflows, user "
            "support, and maintaining a healthy community environment."
        ),
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "email": "staff.three@example.com",
        "first_name": "Charlotte",
        "last_name": "Taylor",
        "nickname": "charlotte_staff",
        "bio": (
            "Community administrator interested in improving user experience, "
            "reviewing reported content, and supporting platform operations."
        ),
        "is_staff": True,
        "is_superuser": False,
    },
    {
        "email": "admin@example.com",
        "first_name": "Admin",
        "last_name": "User",
        "nickname": "platform_admin",
        "bio": (
            "Platform administrator account used for development, testing, "
            "administration, and managing the Social Media API."
        ),
        "is_staff": True,
        "is_superuser": True,
    },
]


class Command(BaseCommand):
    help = "Generate fixture with users and profiles."

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        user_model = get_user_model()
        now = timezone.now()
        fixture = []

        for index, profile_data in enumerate(PROFILES, start=1):
            joined_at = now - timedelta(
                days=random.randint(10, 365),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            user = user_model(
                id=index,
                email=profile_data["email"],
                first_name=profile_data["first_name"],
                last_name=profile_data["last_name"],
                is_staff=profile_data["is_staff"],
                is_superuser=profile_data["is_superuser"],
                is_active=True,
                date_joined=joined_at,
            )
            user.set_password(PROFILE_FIXTURE_PASSWORD)

            profile_id = Profile._meta.pk.default()

            fixture.append(
                {
                    "model": "user.user",
                    "pk": index,
                    "fields": {
                        "password": user.password,
                        "last_login": None,
                        "is_superuser": profile_data["is_superuser"],
                        "first_name": profile_data["first_name"],
                        "last_name": profile_data["last_name"],
                        "is_staff": profile_data["is_staff"],
                        "is_active": True,
                        "date_joined": joined_at.isoformat(),
                        "email": profile_data["email"],
                        "groups": [],
                        "user_permissions": [],
                    },
                }
            )

            fixture.append(
                {
                    "model": "user.profile",
                    "pk": str(profile_id),
                    "fields": {
                        "user": index,
                        "nickname": profile_data["nickname"],
                        "bio": profile_data["bio"],
                        "avatar": "",
                        "created_at": joined_at.isoformat(),
                        "updated_at": joined_at.isoformat(),
                    },
                }
            )

        fixture_path = (
            Path(settings.BASE_DIR)
            / "user"
            / "fixtures"
            / "profiles_fixture.json"
        )

        fixture_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with fixture_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                fixture,
                file,
                indent=2,
                ensure_ascii=False,
            )

        regular_users_count = sum(
            not profile["is_staff"] and not profile["is_superuser"]
            for profile in PROFILES
        )
        staff_users_count = sum(
            profile["is_staff"] and not profile["is_superuser"]
            for profile in PROFILES
        )
        superusers_count = sum(
            profile["is_superuser"]
            for profile in PROFILES
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Fixture generated successfully:\n"
                f"- Regular users: {regular_users_count}\n"
                f"- Staff users: {staff_users_count}\n"
                f"- Superusers: {superusers_count}\n"
                f"- Total users: {len(PROFILES)}\n"
                f"- Output: {fixture_path}"
            )
        )
