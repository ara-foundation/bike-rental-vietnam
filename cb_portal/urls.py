from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns


urlpatterns = i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("bike_rental.urls")),
    path("tours/", include("tours.urls", namespace="tours")),
    path("api/v1/", include("api.urls", namespace="api")),
    path('i18n/', include('django.conf.urls.i18n')),
)


# Настройки для режима отладки
if settings.DEBUG:
    import debug_toolbar
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]

