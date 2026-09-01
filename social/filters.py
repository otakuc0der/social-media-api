from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet
from django_filters import rest_framework as filters
from rest_framework.request import Request

from social.models import Comment, Hashtag, Post


class PostFilter(filters.FilterSet):
    def authors_queryset(
        request: Request,
    ) -> QuerySet:
        if request is None:
            return get_user_model().objects.none()

        return (
            get_user_model()
            .objects
            .filter(
                Q(pk=request.user.pk)
                | Q(
                    follower_relations__follower__pk=request.user.pk
                )
            )
            .distinct()
        )

    author = filters.ModelChoiceFilter(
        field_name="author",
        queryset=authors_queryset,
        empty_label="All authors",
    )

    hashtags = filters.ModelMultipleChoiceFilter(
        field_name="hashtags",
        queryset=Hashtag.objects.all(),
        label="Hashtag IDs",
    )

    hashtags_names = filters.CharFilter(
        method="filter_hashtag_names",
        label="Hashtag names (any)",
    )

    hashtags_all_names = filters.CharFilter(
        method="filter_hashtags_all_names",
        label="Hashtag names (all)",
    )

    created_at = filters.DateFromToRangeFilter(
        field_name="created_at",
        label="Created date range",
    )

    published_at = filters.DateFromToRangeFilter(
        field_name="published_at",
        label="Published date range",
    )

    def filter_hashtag_names(
        self,
        queryset: QuerySet[Post],
        name: str,
        value: str,
    ) -> QuerySet[Post]:
        hashtags = [
            hashtag.strip()
            for hashtag in value.split(",")
            if hashtag.strip()
        ]

        return queryset.filter(
            hashtags__name__in=hashtags
        ).distinct()

    def filter_hashtags_all_names(
        self,
        queryset: QuerySet[Post],
        name: str,
        value: str,
    ) -> QuerySet[Post]:
        hashtags = [
            hashtag.strip()
            for hashtag in value.split(",")
            if hashtag.strip()
        ]

        for hashtag in hashtags:
            queryset = queryset.filter(
                hashtags__name__iexact=hashtag
            )

        return queryset.distinct()

    class Meta:
        model = Post
        fields = []


class CommentFilter(filters.FilterSet):
    author = filters.ModelChoiceFilter(
        field_name="author",
        queryset=get_user_model().objects.none(),
        empty_label="All authors",
    )

    created_at = filters.DateFromToRangeFilter(
        field_name="created_at",
    )

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        author_ids = (
            self.queryset
            .values_list(
                "author_id",
                flat=True,
            )
            .distinct()
        )

        self.filters["author"].queryset = (
            get_user_model()
            .objects
            .filter(pk__in=author_ids)
        )

    class Meta:
        model = Comment
        fields = []
