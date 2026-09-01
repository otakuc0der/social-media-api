import json
import random
from datetime import timedelta
from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from social.models import Like, Post

MIN_LIKES_PER_USER = 3
MAX_LIKES_PER_USER = 8


class Command(BaseCommand):
    help = "Generate fixture with likes for existing users and posts."

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        user_model = get_user_model()

        users = list(
            user_model.objects.prefetch_related(
                "following_relations",
            ).order_by("id")
        )

        if not users:
            self.stdout.write(
                self.style.ERROR(
                    "No users found. Load the profile fixture first."
                )
            )
            return

        posts = list(
            Post.objects.filter(
                status=Post.Status.PUBLISHED,
            ).order_by("created_at")
        )

        if not posts:
            self.stdout.write(
                self.style.ERROR(
                    "No published posts found. "
                    "Load the post fixture first."
                )
            )
            return

        now = timezone.now()
        fixture = []
        likes_count = 0

        posts_by_author: dict[int, list[Post]] = {}

        for post in posts:
            posts_by_author.setdefault(
                post.author_id,
                [],
            ).append(post)

        for user in users:
            following_ids = set(
                user.following_relations.values_list(
                    "following_id",
                    flat=True,
                )
            )

            available_author_ids = {
                user.pk,
                *following_ids,
            }

            available_posts = [
                post
                for author_id in available_author_ids
                for post in posts_by_author.get(
                    author_id,
                    [],
                )
            ]

            if not available_posts:
                self.stdout.write(
                    self.style.WARNING(
                        f"No available posts found for user {user.pk}. "
                        "Skipping."
                    )
                )
                continue

            likes_to_create = min(
                random.randint(
                    MIN_LIKES_PER_USER,
                    MAX_LIKES_PER_USER,
                ),
                len(available_posts),
            )

            selected_posts = random.sample(
                available_posts,
                likes_to_create,
            )

            for post in selected_posts:
                earliest_time = (
                    post.published_at
                    or post.created_at
                    or now
                )

                max_seconds = max(
                    0,
                    int(
                        (
                            now - earliest_time
                        ).total_seconds()
                    ),
                )

                created_at = earliest_time + timedelta(
                    seconds=random.randint(
                        0,
                        max_seconds,
                    )
                    if max_seconds
                    else 0,
                )

                like_id = Like._meta.pk.default()

                fixture.append(
                    {
                        "model": "social.like",
                        "pk": str(like_id),
                        "fields": {
                            "user": user.pk,
                            "post": str(post.pk),
                            "created_at": created_at.isoformat(),
                        },
                    }
                )

                likes_count += 1

        fixture_path = (
            Path(settings.BASE_DIR)
            / "social"
            / "fixtures"
            / "likes_fixture.json"
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
                "Like fixture generated successfully:\n"
                f"- Users: {len(users)}\n"
                f"- Likes: {likes_count}\n"
                f"- Output: {fixture_path}"
            )
        )
