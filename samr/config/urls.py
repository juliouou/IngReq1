"""Enrutamiento principal del proyecto SAMR."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from apps.usuarios.views_ui import login_view, register_view
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # Vistas Frontend (Django Templates)
    path("auth/login/", login_view, name="login_ui"),
    path("auth/register/", register_view, name="register_ui"),

    # Autenticacion JWT
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/verify/", TokenVerifyView.as_view(), name="token_verify"),

    # Documentacion OpenAPI / Swagger / Redoc
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),

    # APIs por aplicacion
    path("api/usuarios/", include("apps.usuarios.urls")),
    path("api/triaje/", include("apps.triaje.urls")),
    path("api/biometria/", include("apps.biometria.urls")),
    path("api/teleconsulta/", include("apps.teleconsulta.urls")),
    path("api/auditoria/", include("apps.auditoria.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
