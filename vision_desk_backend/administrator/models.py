from django.contrib.auth.models import AbstractUser
from django.db import models
from enum import Enum


class User(AbstractUser):
    # Boolean fields to select the type of account.
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class WorkPlaceMetadata(models.Model):
    # Metadata for the workplace
    workplace_image = models.ImageField(upload_to="images/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    workplace_start_time = models.TimeField(blank=True, null=True)
    workplace_end_time = models.TimeField(blank=True, null=True)


class WorkDesk(models.Model):
    # Model for the work desk
    workplace = models.ForeignKey(WorkPlaceMetadata, on_delete=models.CASCADE)
    desk_number = models.CharField(max_length=100)
    x1_coordinate = models.IntegerField()
    y1_coordinate = models.IntegerField()
    x2_coordinate = models.IntegerField()
    y2_coordinate = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.desk_number


class DeskStatusEnum(Enum):
    EMPTY = 0
    IDLE = 1
    WORKING = 2

    @classmethod
    def choices(cls):
        return [(key.name, key.name) for key in cls]


class WorkDeskStatus(models.Model):
    # Model for the work desk status
    workdesk = models.ForeignKey(WorkDesk, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=10,
        choices=DeskStatusEnum.choices(),
        default=DeskStatusEnum.EMPTY.name,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField()

    def __str__(self):
        return f"{self.workdesk.desk_number} - {'Occupied' if self.is_occupied else 'Available'}"
