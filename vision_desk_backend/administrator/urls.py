from administrator.views import SetupWorkPlaceView, ProfileView, ReportAPIView
from django.urls import path

urlpatterns = [
    path("setup-workplace/", SetupWorkPlaceView.as_view(), name="setup_workplace"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("report/", ReportAPIView.as_view(), name="report"),
]
