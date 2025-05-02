from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.http import StreamingHttpResponse
import redis


r = redis.Redis(host="localhost", port=6379, db=5)


class StreamHandlerView(APIView):
    permission_classes = [BasePermission]

    def stream_latest_frame(self):
        while True:
            frame = r.get("latest_frame")
            if frame:
                yield (
                    b"--frame\r\n" b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n"
                )

    def get(self, request, *args, **kwargs):
        if request.GET.get("action") == "stream":
            return StreamingHttpResponse(
                self.stream_latest_frame(),
                content_type="multipart/x-mixed-replace; boundary=frame",
            )
        if request.GET.get("action") == "analytics":
            # Perform analysis logic here
            # For example, you can return a JSON response with analysis results
            analysis_result = {"result": "Analysis result goes here"}
            return JsonResponse(analysis_result, status=status.HTTP_200_OK)
