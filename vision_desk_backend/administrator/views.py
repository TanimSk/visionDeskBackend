import cv2
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from utils.draw_heatmap import generate_status_heatmap

# models
from administrator.models import WorkPlaceMetadata, WorkDeskStatus

# serializers
from administrator.serializers import WorkPlaceMetadataSerializer, WorkDeskSerializer


# pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 500
    page_query_param = "p"


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkPlaceMetadataSerializer
    pagination_class = StandardResultsSetPagination

    def get(self, request, *args, **kwargs):
        workplace_metadata = WorkPlaceMetadata.objects.first()
        if workplace_metadata:
            serializer = self.serializer_class(workplace_metadata)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Workplace metadata not found.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )


class SetupWorkPlaceView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WorkPlaceMetadataSerializer

    def get(self, request, *args, **kwargs):
        if request.GET.get("action") == "get-image":
            workplace_metadata = WorkPlaceMetadata.objects.first()
            if workplace_metadata:
                return FileResponse(
                    open(workplace_metadata.workplace_image.path, "rb"),
                    content_type="image/jpeg",
                )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Workplace metadata not found.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

    def post(self, request, *args, **kwargs):
        if request.GET.get("action") == "add-image":
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid(raise_exception=True):
                # if the workplace metadata already exists, update it
                workplace_metadata = WorkPlaceMetadata.objects.first()
                if workplace_metadata:
                    serializer.update(workplace_metadata, serializer.validated_data)
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Workplace metadata updated successfully.",
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    serializer.save(user=request.user)

                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Workplace metadata created successfully.",
                        },
                        status=status.HTTP_201_CREATED,
                    )

        elif request.GET.get("action") == "add-desks":
            serializer = WorkDeskSerializer(data=request.data, many=True)
            workplace_metadata = WorkPlaceMetadata.objects.first()
            # delete all existing work desks before adding new ones
            if workplace_metadata:
                # delete all existing work desks
                workplace_metadata.workdesk.all().delete()

            if serializer.is_valid(raise_exception=True):
                serializer.save(workplace=workplace_metadata)
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Work desks created successfully.",
                    },
                    status=status.HTTP_201_CREATED,
                )

        elif request.GET.get("action") == "set-time":
            if (
                request.data.get("workplace_start_time")
                and request.data.get("workplace_end_time")
                and request.data.get("source")
            ):
                workplace_metadata = WorkPlaceMetadata.objects.first()
                if workplace_metadata:
                    workplace_metadata.workplace_start_time = request.data.get(
                        "workplace_start_time"
                    )
                    workplace_metadata.workplace_end_time = request.data.get(
                        "workplace_end_time"
                    )
                    workplace_metadata.source = request.data.get("source")
                    workplace_metadata.save()
                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Workplace start and end time updated successfully.",
                        },
                        status=status.HTTP_201_CREATED,
                    )
                else:
                    return JsonResponse(
                        {
                            "success": False,
                            "message": "Workplace metadata not found.",
                        },
                        status=status.HTTP_404_NOT_FOUND,
                    )
            else:
                return JsonResponse(
                    {
                        "success": False,
                        "message": "Workplace start, end time and source fields are required.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        else:
            return JsonResponse(
                {
                    "success": False,
                    "message": "Invalid action.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ReportAPIView(APIView):
    def get(self, request, *args, **kwargs):
        if request.GET.get("type") == "heatmap":
            desk_statuses = WorkDeskStatus.objects.filter(
                created_at__date__gte=timezone.datetime.strptime(
                    request.GET.get("start"), "%Y-%m-%d"
                ).date(),
                created_at__date__lte=timezone.datetime.strptime(
                    request.GET.get("end"), "%Y-%m-%d"
                ).date(),
            ).order_by("created_at")

            if not desk_statuses.exists():
                return JsonResponse(
                    {
                        "success": False,
                        "message": "No data found for the given date range.",
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            desk_location_with_status = []

            for desk_status in desk_statuses:
                desk_location_with_status.append(
                    (
                        (
                            desk_status.workdesk.x1_coordinate,
                            desk_status.workdesk.y1_coordinate,
                            desk_status.workdesk.x2_coordinate,
                            desk_status.workdesk.y2_coordinate,
                        ),
                        desk_status.status,
                    )
                )

            print(desk_location_with_status, desk_status.workdesk.desk_number)

            result_img = generate_status_heatmap(
                cv2.imread(WorkPlaceMetadata.objects.first().workplace_image.path),
                desk_location_with_status,
            )
            _, img_encoded = cv2.imencode(".jpg", result_img)
            return HttpResponse(
                img_encoded.tobytes(),
                content_type="image/jpeg",
            )

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid action.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    def post(self, request, *args, **kwargs):
        # check if the user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse(
                {
                    "success": False,
                    "message": "User is not authenticated.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if request.GET.get("type") == "report":
            desk_statuses = WorkDeskStatus.objects.filter(
                created_at__date__gte=timezone.datetime.strptime(
                    request.GET.get("start"), "%Y-%m-%d"
                ).date(),
                created_at__date__lte=timezone.datetime.strptime(
                    request.GET.get("end"), "%Y-%m-%d"
                ).date(),
            ).order_by("created_at")

            total_working = desk_statuses.filter(status="WORKING").count()
            total_idle = desk_statuses.filter(status="IDLE").count()
            total_empty = desk_statuses.filter(status="EMPTY").count()

            working_percentage = (
                (total_working / desk_statuses.count()) * 100
                if desk_statuses.count() > 0
                else 0
            )
            idle_percentage = (
                (total_idle / desk_statuses.count()) * 100
                if desk_statuses.count() > 0
                else 0
            )
            empty_percentage = (
                (total_empty / desk_statuses.count()) * 100
                if desk_statuses.count() > 0
                else 0
            )

            # get total time for each status, total time is the sum of updated_at - created_at
            total_time_working = sum(
                [
                    (desk_status.updated_at - desk_status.created_at).total_seconds()
                    for desk_status in desk_statuses
                    if desk_status.status == "WORKING"
                ]
            )
            total_time_idle = sum(
                [
                    (desk_status.updated_at - desk_status.created_at).total_seconds()
                    for desk_status in desk_statuses
                    if desk_status.status == "IDLE"
                ]
            )
            total_time_empty = sum(
                [
                    (desk_status.updated_at - desk_status.created_at).total_seconds()
                    for desk_status in desk_statuses
                    if desk_status.status == "EMPTY"
                ]
            )

            # score each desk based on the time spent in each status, more working time means more score (out of 100)
            #  first get desk numbers and their working time
            desk_scores = {}
            for desk_status in desk_statuses:
                if desk_status.workdesk.desk_number not in desk_scores:
                    desk_scores[desk_status.workdesk.desk_number] = 0
                    if desk_status.status == "WORKING":
                        desk_scores[desk_status.workdesk.desk_number] += (
                            desk_status.updated_at - desk_status.created_at
                        ).total_seconds()

            # now rank the desks based on their working time
            desk_scores = dict(
                sorted(desk_scores.items(), key=lambda item: item[1], reverse=True)
            )

            return JsonResponse(
                {
                    "success": True,
                    "data": {
                        "pie_chart": {
                            "working_percentage": f"{working_percentage:.2f}%",
                            "idle_percentage": f"{idle_percentage:.2f}%",
                            "empty_percentage": f"{empty_percentage:.2f}%",
                        },
                        "bar_chart": {
                            "total_working_time": f"{(total_time_working / 3600):.2f}",
                            "total_idle_time": f"{(total_time_idle / 3600):.2f}",
                            "total_empty_time": f"{(total_time_empty / 3600):.2f}",
                        },
                        "desk_scores": desk_scores,
                    },
                },
                status=status.HTTP_200_OK,
            )

        return JsonResponse(
            {
                "success": False,
                "message": "Invalid action.",
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
