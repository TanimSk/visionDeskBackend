from django.contrib import admin
from administrator.models import WorkPlaceMetadata, WorkDesk, WorkDeskStatus, User


@admin.register(User)
class userAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "is_admin")


@admin.register(WorkPlaceMetadata)
class WorkPlaceMetadataAdmin(admin.ModelAdmin):
    list_display = ("workplace_image", "created_at", "updated_at")


@admin.register(WorkDesk)
class WorkDeskAdmin(admin.ModelAdmin):
    list_display = (
        "workplace",
        "desk_number",
        "x1_coordinate",
        "y1_coordinate",
        "x2_coordinate",
        "y2_coordinate",
        "created_at",
        "updated_at",
    )


@admin.register(WorkDeskStatus)
class WorkDeskStatusAdmin(admin.ModelAdmin):
    list_display = ("workdesk", "status", "created_at", "updated_at")
