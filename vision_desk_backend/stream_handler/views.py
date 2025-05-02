from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.http import StreamingHttpResponse
from django.utils import timezone
import redis


# models
from administrator.models import WorkDeskStatus, WorkPlaceMetadata, DeskStatusEnum


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

        if request.GET.get("action") == "desk-analytics" and request.GET.get("desk-no"):
            graph_data = {
                "labels": [],
                "status": [],
            }
            desk_status = WorkDeskStatus.objects.filter(
                workdesk__desk_number=request.GET.get("desk-no"),
                created_at__date=timezone.localtime().date(),
            ).order_by("-created_at")

            for desk_status in desk_status:
                graph_data["labels"].append(desk_status.created_at.strftime("%H:%M"))
                graph_data["status"].append(DeskStatusEnum(desk_status.status).value)

            return JsonResponse(
                graph_data,
                status=status.HTTP_200_OK,
            )

        if request.GET.get("action") == "analytics":

            # timeline graph
            timeline = []
            workplace_info = WorkPlaceMetadata.objects.first()
            start_time = workplace_info.workplace_start_time
            end_time = workplace_info.workplace_end_time

            # Combine with today's date to create datetime objects
            current_datetime = timezone.datetime.combine(
                timezone.datetime.today(), start_time
            )
            end_datetime = timezone.datetime.combine(
                timezone.datetime.today(), end_time
            )

            while current_datetime < end_datetime:
                time_only = current_datetime.time()

                work_status_filtered = WorkDeskStatus.objects.filter(
                    created_at__hour__lte=current_datetime.hour,
                    created_at__hour__gte=current_datetime.hour - 1,
                )

                total_count = work_status_filtered.count()

                timeline.append(
                    {
                        "time": f"{time_only.strftime("%H:%M")}",
                        "idle": f"{((work_status_filtered.filter(status='IDLE').count() / total_count) *100) if total_count != 0 else 0}%",
                        "working": f"{((work_status_filtered.filter(status='WORKING').count() / total_count) *100)  if total_count != 0 else 0}%",
                        "empty": f"{((work_status_filtered.filter(status='EMPTY').count() / total_count) *100)if total_count != 0 else 0}%",
                    }
                )

                current_datetime += timezone.timedelta(hours=1)

            return JsonResponse(
                {
                    "timeline": timeline,
                },
                status=status.HTTP_200_OK,
            )
