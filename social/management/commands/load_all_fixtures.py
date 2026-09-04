from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command


class Command(BaseCommand):
    help = "Generate and load all project fixtures in dependency order."

    FIXTURES = (
        (
            "generate_profiles_fixture",
            Path("user") / "fixtures" / "profiles_fixture.json",
        ),
        (
            "generate_hashtags_fixture",
            Path("social") / "fixtures" / "hashtags_fixture.json",
        ),
        (
            "generate_follows_fixture",
            Path("user") / "fixtures" / "follows_fixture.json",
        ),
        (
            "generate_posts_fixture",
            Path("social") / "fixtures" / "posts_fixture.json",
        ),
        (
            "generate_likes_fixture",
            Path("social") / "fixtures" / "likes_fixture.json",
        ),
        (
            "generate_comments_fixture",
            Path("social") / "fixtures" / "comments_fixture.json",
        ),
    )

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        for command_name, relative_fixture_path in self.FIXTURES:
            fixture_path = (
                Path(settings.BASE_DIR)
                / relative_fixture_path
            )

            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"Running {command_name}..."
                )
            )

            call_command(
                command_name,
            )

            if not fixture_path.exists():
                raise CommandError(
                    f"Fixture was not generated: {fixture_path}"
                )

            self.stdout.write(
                self.style.MIGRATE_HEADING(
                    f"Loading {fixture_path.name}..."
                )
            )

            call_command(
                "loaddata",
                str(fixture_path),
            )

        self.stdout.write(
            self.style.SUCCESS(
                "All fixtures generated and loaded successfully."
            )
        )
