from administrator.views import SetupWorkPlaceView, ProfileView
from django.urls import path

urlpatterns = [
    path("setup-workplace/", SetupWorkPlaceView.as_view(), name="setup_workplace"),
    path("profile/", ProfileView.as_view(), name="profile"),
]
