from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/socials/", include("social.urls", namespace="social")),
    path("api/users/", include("user.urls", namespace="user")),
]

if settings.DEBUG:
    urlpatterns.extend(
        [path("__debug__/", include("debug_toolbar.urls")),]
    )

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
