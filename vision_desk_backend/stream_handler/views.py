from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.http import StreamingHttpResponse
from django.utils import timezone
import redis
import json
from utils.buffer import StatusBuffer

# models
from administrator.models import (
    WorkDeskStatus,
    WorkPlaceMetadata,
    DeskStatusEnum,
    WorkDesk,
)

# serializers
from administrator.serializers import WorkDeskSerializer

r = redis.Redis(host="localhost", port=6379, db=5)
status_buffer = StatusBuffer()


class UpdateBoudingBoxesView(APIView):
    """
    Example:
    {
        "n_person": 4,
        "n_tables": 5,
        "person_in_the_table": 1,
        "person_idle": 2,
        "person_away": 2,
        "person_bound_boxes": {
            "0": [120, 180, 200, 260],
        },
        "person_status": {
            "0": 1,
            "1": 0,
            "2": 1,
            "3": 0
        },
        "desk_person_map": {
            "0": 1,
            "1": 3,
            "2": -1,
            "3": -1,
            "4": 0
        }
    }
    """

    def post(self, request, *args, **kwargs):
        # Store the bounding boxes in Redis
        r.set("latest_bounding_boxes", json.dumps(request.data))

        print("latest_bounding_boxes", request.data)

        desk_status_map = []

        # map the desk number with the status
        for desk_no, person in request.data["desk_person_map"].items():
            print(desk_no, person)
            if person == -1:  # no person in the desk
                continue
            desk_status_map.append(
                {
                    "desk_no": desk_no,
                    "status_enum": request.data["person_status"][str(person)],
                }
            )

        # add the status to the buffer
        for desk_status in desk_status_map:
            status_buffer.add_status(
                desk_no=desk_status["desk_no"],
                status_enum=desk_status["status_enum"],
            )

        return Response(
            {"message": "Bounding boxes updated successfully."},
            status=status.HTTP_200_OK,
        )


class StreamHandlerView(APIView):
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

        # check if the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "success": False,
                    "message": "User is not authenticated.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if request.GET.get("action") == "desk-analytics":
            if request.GET.get("desk-no"):
                all_desk_no = list(
                    WorkDesk.objects.all()
                    .order_by("desk_number")
                    .values_list("desk_number", flat=True)
                )

                graph_data = {
                    "total": len(all_desk_no),
                    "next_desk": all_desk_no[
                        (all_desk_no.index(request.GET.get("desk-no")) + 1)
                        % len(all_desk_no)
                    ],
                    "prev_desk": all_desk_no[
                        (all_desk_no.index(request.GET.get("desk-no")) - 1)
                        % len(all_desk_no)
                    ],
                    "desk_info": {},
                    "labels": [],
                    "status": [],
                }
                desk_status = WorkDeskStatus.objects.filter(
                    workdesk__desk_number=request.GET.get("desk-no"),
                    created_at__date=timezone.localtime().date(),
                ).order_by("-created_at")

                # desk info
                graph_data["desk_info"] = WorkDeskSerializer(
                    WorkDesk.objects.get(desk_number=request.GET.get("desk-no"))
                ).data

                for desk_status in desk_status:
                    graph_data["labels"].append(
                        desk_status.created_at.strftime("%h:%M %p")
                    )
                    graph_data["status"].append(desk_status.status)

                return JsonResponse(
                    graph_data,
                    status=status.HTTP_200_OK,
                )

            desks = WorkDesk.objects.all()
            return Response(
                WorkDeskSerializer(desks, many=True).data,
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
                        "idle": f"{(((work_status_filtered.filter(status='IDLE').count() / total_count) *100) if total_count != 0 else 0):.2f}%",
                        "working": f"{(((work_status_filtered.filter(status='WORKING').count() / total_count) *100)  if total_count != 0 else 0):.2f}%",
                        "empty": f"{(((work_status_filtered.filter(status='EMPTY').count() / total_count) *100)if total_count != 0 else 0):.2f}%",
                    }
                )

                current_datetime += timezone.timedelta(hours=1)

            return JsonResponse(
                {
                    "timeline": timeline,
                },
                status=status.HTTP_200_OK,
            )
