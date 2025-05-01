from administrator.views import SetupWorkPlaceView
from django.urls import path

urlpatterns = [
    path("setup-workplace/", SetupWorkPlaceView.as_view(), name="setup_workplace"),
]