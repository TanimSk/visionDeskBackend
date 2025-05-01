from django.urls import path, include
from .views import StreamHandlerView

urlpatterns = [
    path('get-stream/',  StreamHandlerView.as_view(), name='stream_handler'),
]