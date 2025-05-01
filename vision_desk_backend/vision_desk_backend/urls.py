from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView
from dj_rest_auth.registration.views import VerifyEmailView
from rest_framework_simplejwt.views import TokenVerifyView
from dj_rest_auth.views import (
    PasswordResetConfirmView,
    PasswordResetView,
    PasswordChangeView,
)
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from administrator.auth_view import LoginWthPermission


urlpatterns = [
    path("admin/", admin.site.urls),
    # ---------- Auth ------------
    path("rest-auth/login/", LoginWthPermission.as_view(), name="login_view"),
    # Password Change
    # path(
    #     "rest-auth/password/change/",
    #     CustomPasswordChangeView.as_view(),
    #     name="password_change",
    # ),
    path("rest-auth/", include("dj_rest_auth.urls")),
    path(
        "rest-auth/registration/account-confirm-email/",
        VerifyEmailView.as_view(),
        name="account_email_verification_sent",
    ),
    path("rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    # Password Reset
    path(
        "rest-auth/password/reset/", PasswordResetView.as_view(), name="password_reset"
    ),
    path(
        "rest-auth/password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="rest_password_reset_confirm",
    ),
    path(
        "rest-auth/password/reset/confirm/<str:uidb64>/<str:token>",
        TemplateView.as_view(),
        name="password_reset_confirm",
    ),
    path("get-access-token/", TokenRefreshView.as_view(), name="get-access-token"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    # ---------- End Auth ---------- 
    path("stream/", include("stream_handler.urls")),
    path("administrator/", include("administrator.urls")),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)