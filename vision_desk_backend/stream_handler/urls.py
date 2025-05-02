from django.urls import path, include
from .views import StreamHandlerView

urlpatterns = [
    path('realtime-data/',  StreamHandlerView.as_view(), name='stream_handler'),
]