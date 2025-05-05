from dj_rest_auth.registration.views import LoginView
from django.contrib.auth import login as django_login
from rest_framework.response import Response
from rest_framework.views import APIView

# from rest_framework.permissions import BasePermission, IsAuthenticated
# from dj_rest_auth.views import PasswordChangeView
from rest_framework import status

# models
from administrator.models import WorkPlaceMetadata

# authentication
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate


class LoginWthPermission(APIView):
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")

        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        if not user:
            return Response(
                {
                    "success": False,
                    "message": "Invalid credentials",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)

        # Construct the response
        response_data = {
            "success": True,
            "access": access_token,
            "refresh": str(refresh),
            "user": {
                "pk": user.pk,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            "role": "ADMIN" if user.is_admin else "UNKNOWN",
            "workplace_setup": WorkPlaceMetadata.objects.exists(),
        }

        # Development only: don't use samesite=None or secure=True
        # Set access and refresh token to the cookie
        response = Response(response_data, status=status.HTTP_200_OK)
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="None",
            max_age=60 * 60 * 24 * 7,  # 1 week
        )
        response.set_cookie(
            key="refresh_token",
            value=str(refresh),
            httponly=True,
            secure=False,
            samesite="None",
            max_age=60 * 60 * 24 * 30,  # 1-month expiration
        )
        return response


class CustomLogout(APIView):
    def post(self, request):
        # Delete JWT token from the cookie
        response = Response(
            {"success": True, "message": "Logged out successfully"},
            status=status.HTTP_200_OK,
        )

        # Set cookies to expire immediately
        response.set_cookie(
            "access_token",
            "",
            expires=0,
            path="/",
            httponly=True,
            secure=True,
            samesite="None",
        )
        response.set_cookie(
            "refresh_token",
            "",
            expires=0,
            path="/",
            httponly=True,
            secure=True,
            samesite="None",
        )

        # Ensure they are deleted
        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        return response
