import json
import random
from datetime import timedelta
from pathlib import Path
from typing import Any

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from social.models import Comment, Post

MIN_COMMENTS_PER_USER = 2
MAX_COMMENTS_PER_USER = 6


COMMENT_TEMPLATES = [
    "Really enjoyed this post. Thanks for sharing!",
    "This is a great point.",
    "I completely agree with this.",
    "That sounds like a great experience.",
    "Thanks for sharing this!",
    "Interesting perspective. I had not thought about it that way.",
    "This looks amazing!",
    "Definitely adding this to my list.",
    "I have been thinking about the same thing recently.",
    "Great post!",
    "That is really useful advice.",
    "I would love to try this sometime.",
    "This reminds me of a similar experience I had recently.",
    "Really interesting. Would love to hear more about this.",
    "Nice! Looking forward to seeing what comes next.",
    "This is exactly the kind of thing I needed to read today.",
    "Good reminder. It is easy to forget this.",
    "I like this approach.",
    "Sounds like time well spent.",
    "Thanks for the recommendation!",
]


class Command(BaseCommand):
    help = "Generate fixture with comments for existing users and posts."

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
        comments_count = 0

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

            comments_to_create = random.randint(
                MIN_COMMENTS_PER_USER,
                MAX_COMMENTS_PER_USER,
            )

            for _ in range(comments_to_create):
                post = random.choice(
                    available_posts,
                )

                content = random.choice(
                    COMMENT_TEMPLATES,
                )

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

                comment_id = Comment._meta.pk.default()

                fixture.append(
                    {
                        "model": "social.comment",
                        "pk": str(comment_id),
                        "fields": {
                            "author": user.pk,
                            "post": str(post.pk),
                            "content": content,
                            "created_at": created_at.isoformat(),
                            "updated_at": created_at.isoformat(),
                        },
                    }
                )

                comments_count += 1

        fixture_path = (
            Path(settings.BASE_DIR)
            / "social"
            / "fixtures"
            / "comments_fixture.json"
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
                "Comment fixture generated successfully:\n"
                f"- Users: {len(users)}\n"
                f"- Comments: {comments_count}\n"
                f"- Output: {fixture_path}"
            )
        )
