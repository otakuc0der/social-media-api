from django.urls import path, include
from rest_framework.routers import DefaultRouter

from user.views import (
    CreateTokenView,
    CreateUserView,
    LogoutView,
    ManageUserView,
    ProfilesReadOnlyViewSet,
)

app_name = "user"


router = DefaultRouter()
router.register(prefix="profiles", viewset=ProfilesReadOnlyViewSet, basename="profile")

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="create"),
    path("login/", CreateTokenView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", ManageUserView.as_view(), name="manage"),
    path("", include(router.urls)),
]
