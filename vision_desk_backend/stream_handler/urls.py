from django.urls import path, include
from .views import StreamHandlerView, UpdateBoudingBoxesView

urlpatterns = [
    path("realtime-data/", StreamHandlerView.as_view(), name="stream_handler"),
    path("update-bounding-boxes/", UpdateBoudingBoxesView.as_view(), name="update_bounding_boxes"),
]
