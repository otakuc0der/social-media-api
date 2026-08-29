from django_filters import rest_framework as filters

from user.models import Profile


class ProfileFilter(filters.FilterSet):
    nickname = filters.CharFilter(field_name="nickname", lookup_expr="icontains")
    email = filters.CharFilter(field_name="user__email", lookup_expr="icontains")
    first_name = filters.CharFilter(field_name="user__first_name", lookup_expr="icontains")
    last_name = filters.CharFilter(field_name="user__last_name", lookup_expr="icontains")

    class Meta:
        model = Profile
        fields = []
