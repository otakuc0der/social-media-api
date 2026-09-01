import json
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand

from social.models import Hashtag

HASHTAGS = [
    "travel",
    "books",
    "reading",
    "programming",
    "python",
    "django",
    "technology",
    "cooking",
    "food",
    "photography",
    "fitness",
    "running",
    "music",
    "art",
    "design",
    "hiking",
    "nature",
    "gardening",
    "lifestyle",
    "movies",
    "gaming",
    "education",
    "productivity",
    "health",
    "sports",
    "pets",
    "fashion",
    "science",
    "news",
    "inspiration",
]


class Command(BaseCommand):
    help = "Generate fixture with hashtags."

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        fixture = []

        for hashtag_name in HASHTAGS:
            hashtag_id = Hashtag._meta.pk.default()

            fixture.append(
                {
                    "model": "social.hashtag",
                    "pk": str(hashtag_id),
                    "fields": {
                        "name": hashtag_name,
                    },
                }
            )

        fixture_path = (
            Path(settings.BASE_DIR) / "social" / "fixtures" / "hashtags_fixture.json"
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
                "Hashtag fixture generated successfully:\n"
                f"- Hashtags: {len(HASHTAGS)}\n"
                f"- Output: {fixture_path}"
            )
        )
