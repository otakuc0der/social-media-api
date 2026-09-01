import json
import random
from datetime import timedelta
from pathlib import Path
from typing import Any

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from social.models import Hashtag, Post
from user.models import Profile

MIN_POSTS_PER_PROFILE = 3
MAX_POSTS_PER_PROFILE = 6
MIN_HASHTAGS_PER_POST = 1
MAX_HASHTAGS_PER_POST = 3


PROFILE_POSTS = {
    "alex_travels": [
        (
            "Spent the morning walking through small streets away from the "
            "usual tourist routes. The best part of travelling is often "
            "finding places you never planned to visit."
        ),
        (
            "One thing I always do in a new city is visit the local market. "
            "It tells you a lot about the people, food, and everyday life."
        ),
        (
            "Another trip added to the list. Great views, long walks, and "
            "probably too many photos taken along the way."
        ),
        (
            "Planning the next weekend trip. Trying to choose between "
            "mountains, a quiet old town, or somewhere near the coast."
        ),
        (
            "Travel tip: leave some free time in your itinerary. Some of the "
            "best moments happen when you are not rushing to the next place."
        ),
        (
            "Found a small viewpoint just before sunset today. Definitely one "
            "of those places I would happily return to."
        ),
    ],
    "emma_reads": [
        (
            "Finished a novel that started slowly but became impossible to put "
            "down halfway through. Sometimes patience with a book really pays off."
        ),
        (
            "My reading list keeps growing faster than I can finish books. "
            "Currently deciding what should be next."
        ),
        (
            "There is something especially satisfying about finding a book you "
            "want to recommend immediately after finishing it."
        ),
        (
            "Re-reading an old favourite this week. It is interesting how the "
            "same story can feel completely different a few years later."
        ),
        (
            "Trying to read more non-fiction this month. I want something that "
            "teaches me something new without feeling like a textbook."
        ),
        (
            "A quiet evening, coffee, and a good book is still one of the best "
            "ways to end the day."
        ),
    ],
    "daniel_codes": [
        (
            "Spent some time refactoring an API today. The final code is "
            "shorter, but the real improvement is that the responsibilities "
            "are much clearer now."
        ),
        (
            "Writing tests before touching a complicated piece of logic makes "
            "refactoring much less stressful."
        ),
        (
            "Working with Django REST Framework again today. Good serializers "
            "and clear validation rules make API code much easier to maintain."
        ),
        (
            "Small reminder to myself: database queries matter. A feature can "
            "work correctly and still perform badly because of unnecessary queries."
        ),
        (
            "Learning more about service layers and where business logic should "
            "live in larger Django projects."
        ),
        (
            "Sometimes the best debugging tool is simply reducing the problem "
            "to the smallest reproducible example."
        ),
    ],
    "sophia_cooks": [
        (
            "Made a simple pasta dinner with tomatoes, garlic, herbs, and a lot "
            "of parmesan. Nothing complicated, but exactly what I wanted."
        ),
        (
            "Trying a new bread recipe today. The kitchen already smells better "
            "than expected."
        ),
        (
            "Cooking becomes much easier when a few basic ingredients are "
            "always available at home."
        ),
        (
            "Experimented with roasted vegetables and a homemade sauce tonight. "
            "Definitely adding this combination to the regular rotation."
        ),
        (
            "Weekend baking experiment was a success. Slightly uneven, but "
            "taste matters more than perfect presentation."
        ),
        (
            "Fresh herbs can completely change a simple meal. I should probably "
            "start growing more of them at home."
        ),
    ],
    "mike_frames": [
        (
            "Went out with the camera just before sunset. The city looks "
            "completely different when the light starts changing."
        ),
        (
            "Street photography is mostly about patience. Sometimes you wait "
            "ten minutes for one interesting moment."
        ),
        (
            "Architecture, reflections, and rainy streets made today's photo "
            "walk much more interesting than expected."
        ),
        (
            "Trying to pay more attention to shadows and small details instead "
            "of always looking for large scenes."
        ),
        ("The best camera walk is usually the one without a strict route."),
        (
            "Edited a few older photos today and found several frames I had "
            "completely overlooked the first time."
        ),
    ],
    "olivia_moves": [
        (
            "Finished today's strength session. Progress feels slow sometimes, "
            "but consistency keeps adding up."
        ),
        ("Easy run this morning. No pace goal, just movement and fresh air."),
        (
            "Rest days are part of training too. Still learning not to feel "
            "guilty about taking them."
        ),
        (
            "A short workout is still better than skipping movement completely "
            "on a busy day."
        ),
        (
            "Tracking progress over several months is much more useful than "
            "judging one workout."
        ),
        ("Trying to improve mobility alongside strength training this month."),
    ],
    "ethan_music": [
        (
            "Found an album today that I somehow missed when it was released. "
            "It has been on repeat all evening."
        ),
        (
            "Practising guitar slowly is less exciting, but it fixes mistakes "
            "much faster than trying to play everything at full speed."
        ),
        (
            "Building another playlist for late-night work sessions. It already "
            "has far too many songs."
        ),
        (
            "Live recordings sometimes capture a song better than the studio "
            "version. The extra energy changes everything."
        ),
        ("Trying to learn a song by ear instead of looking up the chords."),
        (
            "Music discovery is one of the reasons I still enjoy making themed "
            "playlists instead of just using automatic recommendations."
        ),
    ],
    "mia_creates": [
        (
            "Working on a new illustration and trying to keep the composition "
            "simple before adding details."
        ),
        (
            "Some sketches never become finished pieces, but they still teach "
            "you something useful."
        ),
        (
            "Experimenting with typography today. Small spacing changes make a "
            "much bigger difference than expected."
        ),
        (
            "Trying a different drawing workflow this week: fewer layers and "
            "more decisions made early."
        ),
        ("Collected a few colour and layout references for the next project."),
        (
            "Finished an illustration that changed direction three times before "
            "finally feeling right."
        ),
    ],
    "noah_outdoors": [
        (
            "Weekend hike completed. Long climb, cold wind near the top, and "
            "absolutely worth it for the view."
        ),
        ("Testing a lighter backpack setup for shorter trips this season."),
        (
            "Nothing resets the brain quite like spending several hours away "
            "from roads, notifications, and screens."
        ),
        (
            "Found a new trail today that I definitely want to explore again "
            "when the weather changes."
        ),
        (
            "Checking equipment before a trip is boring until the moment you "
            "realise you forgot something important."
        ),
        (
            "Early starts are painful, but quiet trails in the morning make "
            "them worth it."
        ),
    ],
    "ava_foodie": [
        (
            "Tried a small neighbourhood cafe today and found one of the best "
            "breakfasts I have had recently."
        ),
        (
            "A good restaurant does not need a huge menu. A few dishes done "
            "really well are usually enough."
        ),
        (
            "Found another place worth returning to: simple food, friendly "
            "service, and excellent coffee."
        ),
        (
            "Trying more local dishes whenever I visit a new place has become "
            "one of my favourite travel habits."
        ),
        ("Today's dessert looked almost too good to eat. Almost."),
        (
            "Keeping a list of cafes I want to try was a mistake. It keeps "
            "getting longer every week."
        ),
    ],
    "liam_tech": [
        (
            "Testing a new productivity app today. The interface is clean, but "
            "I am still deciding whether it actually improves the workflow."
        ),
        (
            "Good technology should disappear into the background and make a "
            "task easier without constantly demanding attention."
        ),
        (
            "Reading about recent changes in developer tooling. The ecosystem "
            "moves ridiculously fast."
        ),
        (
            "Spent some time comparing different hardware options today. Specs "
            "matter, but real-world usability usually matters more."
        ),
        (
            "Automation is great until maintaining the automation becomes more "
            "work than the original task."
        ),
        (
            "Trying to simplify the number of tools I use every day instead of "
            "adding another app for every small problem."
        ),
    ],
    "bella_gardens": [
        (
            "A new leaf appeared on one of the plants I thought was struggling. "
            "Apparently patience was the correct solution."
        ),
        (
            "Repotted a few indoor plants today and discovered that I definitely "
            "need more shelf space."
        ),
        (
            "Learning to water plants based on the soil instead of following a "
            "strict schedule has made a huge difference."
        ),
        ("Started a few herbs from seed. Now comes the difficult part: " "waiting."),
        (
            "Trying to make the balcony a little greener before the end of the "
            "season."
        ),
        (
            "Gardening is mostly experimenting, observing what happens, and "
            "trying again when something does not work."
        ),
    ],
    "grace_staff": [
        (
            "Spent some time reviewing community discussions today. Clear rules "
            "make moderation much easier for everyone."
        ),
        (
            "Good online communities depend on both useful tools and reasonable "
            "communication between people."
        ),
        (
            "Testing a few moderation workflows and looking for places where "
            "common actions can be simplified."
        ),
        (
            "Documentation for community rules should be short enough to read "
            "and specific enough to actually help."
        ),
    ],
    "henry_staff": [
        (
            "Working through several user support cases today and documenting "
            "the common issues for future reference."
        ),
        (
            "Small improvements to moderation tools can save a surprising "
            "amount of repetitive work."
        ),
        ("Reviewing platform workflows and looking for unnecessary steps."),
        ("Healthy communities need consistent rules more than complicated rules."),
    ],
    "charlotte_staff": [
        (
            "Reviewing reported content and testing improvements to the admin "
            "workflow today."
        ),
        (
            "A good moderation interface should provide enough context to make "
            "a decision without requiring several extra pages."
        ),
        (
            "Collecting feedback about the current community experience and "
            "turning recurring problems into concrete improvements."
        ),
        ("Consistency is one of the most important parts of moderation."),
    ],
    "platform_admin": [
        (
            "Development environment updated and ready for another round of API "
            "testing."
        ),
        ("Checking platform configuration and reviewing recent backend changes."),
        ("Running maintenance and development checks across the project."),
        ("Another set of API features is ready for testing."),
    ],
}


PROFILE_HASHTAGS = {
    "alex_travels": [
        "travel",
        "photography",
        "nature",
        "lifestyle",
    ],
    "emma_reads": [
        "books",
        "reading",
        "education",
        "inspiration",
    ],
    "daniel_codes": [
        "programming",
        "python",
        "django",
        "technology",
        "education",
    ],
    "sophia_cooks": [
        "cooking",
        "food",
        "lifestyle",
    ],
    "mike_frames": [
        "photography",
        "art",
        "design",
    ],
    "olivia_moves": [
        "fitness",
        "running",
        "health",
        "sports",
    ],
    "ethan_music": [
        "music",
        "art",
        "inspiration",
    ],
    "mia_creates": [
        "art",
        "design",
        "inspiration",
    ],
    "noah_outdoors": [
        "hiking",
        "nature",
        "travel",
        "health",
    ],
    "ava_foodie": [
        "food",
        "cooking",
        "travel",
        "lifestyle",
    ],
    "liam_tech": [
        "technology",
        "programming",
        "productivity",
        "science",
    ],
    "bella_gardens": [
        "gardening",
        "nature",
        "lifestyle",
    ],
    "grace_staff": [
        "news",
        "education",
        "productivity",
    ],
    "henry_staff": [
        "news",
        "technology",
        "productivity",
    ],
    "charlotte_staff": [
        "news",
        "technology",
        "education",
    ],
    "platform_admin": [
        "technology",
        "programming",
        "news",
    ],
}


class Command(BaseCommand):
    help = "Generate fixture with posts for existing profiles."

    def handle(
        self,
        *args: Any,
        **options: Any,
    ) -> None:
        profiles = list(
            Profile.objects.select_related("user").order_by(
                "user_id",
            )
        )

        if not profiles:
            self.stdout.write(
                self.style.ERROR("No profiles found. Load the profile fixture first.")
            )
            return

        hashtags_by_name = {hashtag.name: hashtag for hashtag in Hashtag.objects.all()}

        if not hashtags_by_name:
            self.stdout.write(
                self.style.ERROR("No hashtags found. Load the hashtag fixture first.")
            )
            return

        now = timezone.now()
        fixture = []

        posts_count = 0

        for profile in profiles:
            post_templates = PROFILE_POSTS.get(
                profile.nickname,
            )

            if not post_templates:
                self.stdout.write(
                    self.style.WARNING(
                        "No post templates found for profile "
                        f"'{profile.nickname}'. Skipping."
                    )
                )
                continue

            available_hashtag_names = [
                hashtag_name
                for hashtag_name in PROFILE_HASHTAGS.get(
                    profile.nickname,
                    [],
                )
                if hashtag_name in hashtags_by_name
            ]

            if not available_hashtag_names:
                self.stdout.write(
                    self.style.WARNING(
                        "No matching hashtags found for profile "
                        f"'{profile.nickname}'. Skipping."
                    )
                )
                continue

            posts_to_create = random.sample(
                post_templates,
                random.randint(
                    MIN_POSTS_PER_PROFILE,
                    min(
                        MAX_POSTS_PER_PROFILE,
                        len(post_templates),
                    ),
                ),
            )

            for content in posts_to_create:
                created_at = now - timedelta(
                    days=random.randint(1, 180),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                )

                hashtags_count = random.randint(
                    MIN_HASHTAGS_PER_POST,
                    min(
                        MAX_HASHTAGS_PER_POST,
                        len(available_hashtag_names),
                    ),
                )

                selected_hashtags = random.sample(
                    available_hashtag_names,
                    hashtags_count,
                )

                hashtag_ids = [
                    str(hashtags_by_name[hashtag_name].pk)
                    for hashtag_name in selected_hashtags
                ]

                post_id = Post._meta.pk.default()

                fixture.append(
                    {
                        "model": "social.post",
                        "pk": str(post_id),
                        "fields": {
                            "author": profile.user_id,
                            "content": content,
                            "image": "",
                            "status": Post.Status.PUBLISHED,
                            "scheduled_at": None,
                            "published_at": created_at.isoformat(),
                            "created_at": created_at.isoformat(),
                            "updated_at": created_at.isoformat(),
                            "hashtags": hashtag_ids,
                        },
                    }
                )

                posts_count += 1

        fixture_path = (
            Path(settings.BASE_DIR) / "social" / "fixtures" / "posts_fixture.json"
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
                "Post fixture generated successfully:\n"
                f"- Profiles: {len(profiles)}\n"
                f"- Posts: {posts_count}\n"
                f"- Output: {fixture_path}"
            )
        )
