from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import BasePermission
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

# models
from administrator.models import WorkPlaceMetadata

# serializers
from administrator.serializers import WorkPlaceMetadataSerializer, WorkDeskSerializer


# pagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 500
    page_query_param = "p"


class SetupWorkPlaceView(APIView):
    permission_classes = [BasePermission]
    serializer_class = WorkPlaceMetadataSerializer

    def post(self, request, *args, **kwargs):
        if request.GET.get("action") == "add-image":
            serializer = self.serializer_class(data=request.data)
            if serializer.is_valid():
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
                    serializer.save()

                    return JsonResponse(
                        {
                            "success": True,
                            "message": "Workplace metadata created successfully.",
                        },
                        status=status.HTTP_201_CREATED,
                    )
            else:
                return JsonResponse(
                    {"success": False, "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif request.GET.get("action") == "add-desks":
            serializer = WorkDeskSerializer(data=request.data, many=True)
            if serializer.is_valid():
                serializer.save()
                return JsonResponse(
                    {
                        "success": True,
                        "message": "Work desks created successfully.",
                    },
                    status=status.HTTP_201_CREATED,
                )
            else:
                return JsonResponse(
                    {"success": False, "message": serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        elif request.GET.get("action") == "set-time":
            if request.data.get("workplace_start_time") and request.data.get(
                "workplace_end_time"
            ):
                workplace_metadata = WorkPlaceMetadata.objects.first()
                if workplace_metadata:
                    workplace_metadata.workplace_start_time = request.data.get(
                        "workplace_start_time"
                    )
                    workplace_metadata.workplace_end_time = request.data.get(
                        "workplace_end_time"
                    )
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
                        "message": "Workplace start and end time are required.",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )