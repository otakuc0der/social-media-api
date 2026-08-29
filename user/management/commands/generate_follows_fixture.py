import json
import random
from datetime import timedelta
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from user.models import Follow, User


MIN_FOLLOWING = 2
MAX_FOLLOWING = 6


class Command(BaseCommand):
    help = "Generate fixture with follow relationships."

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        users = list(
            User.objects.order_by("id")
        )

        if len(users) < 2:
            self.stdout.write(
                self.style.ERROR(
                    "At least two users are required to generate follows."
                )
            )
            return

        now = timezone.now()
        fixture = []

        follow_pairs: set[tuple[int, int]] = set()

        for follower in users:
            possible_followings = [
                user
                for user in users
                if user.pk != follower.pk
            ]

            following_count = random.randint(
                MIN_FOLLOWING,
                min(
                    MAX_FOLLOWING,
                    len(possible_followings),
                ),
            )

            selected_users = random.sample(
                possible_followings,
                following_count,
            )

            for following in selected_users:
                pair = (
                    follower.pk,
                    following.pk,
                )

                if pair in follow_pairs:
                    continue

                follow_pairs.add(pair)

                created_at = now - timedelta(
                    days=random.randint(0, 180),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )

                follow_id = Follow._meta.pk.default()

                fixture.append(
                    {
                        "model": "user.follow",
                        "pk": str(follow_id),
                        "fields": {
                            "follower": follower.pk,
                            "following": following.pk,
                            "created_at": created_at.isoformat(),
                        },
                    }
                )

        fixture_path = (
            Path(settings.BASE_DIR)
            / "user"
            / "fixtures"
            / "follows_fixture.json"
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

        self.stdout.write(
            self.style.SUCCESS(
                "Follow fixture generated successfully:\n"
                f"- Users: {len(users)}\n"
                f"- Follow relationships: {len(fixture)}\n"
                f"- Output: {fixture_path}"
            )
        )
