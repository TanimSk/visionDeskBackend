from django.utils import timezone
from administrator.models import WorkDeskStatus, DeskStatusEnum, WorkDesk
from django.utils import timezone


class StatusBuffer:
    FRAMES_LIMIT = 1000

    def __init__(self):
        self.buffer = []
        self.frame_count = 0
        self.all_desk_instances_map = {
            desk.desk_number: desk for desk in WorkDesk.objects.all()
        }

    def add_status(self, desk_no, status_enum):
        self.frame_count += 1
        """
        adds status to the buffer along with the timestamp and desk number.
        if the buffer exceeds the BUFFER_SIZE, it stores the buffer in the database in batches.
        And then clears the buffer.
        """
        if self.frame_count >= self.FRAMES_LIMIT:
            print("Buffer size exceeded, saving to database. (Using Bulk create)")

            WorkDeskStatus.objects.bulk_create(
                [
                    WorkDeskStatus(
                        workdesk=self.all_desk_instances_map.get(data["workdesk"]),
                        status=DeskStatusEnum(data["status_enum"]).name,
                        created_at=data["timestamp"],
                        updated_at=timezone.localtime(timezone.now()),
                    )
                    for data in self.buffer
                ]
            )

            # Clear the buffer after saving to the database
            self.buffer.clear()
            self.frame_count = 0

        # avoid duplicate statues
        if self.buffer and self.buffer[-1]["status_enum"] == status_enum:
            # just update the timestamp
            self.buffer[-1]["timestamp"] = timezone.localtime(timezone.now())
            return

        self.buffer.append(
            {
                "workdesk": desk_no,
                "status_enum": status_enum,
                "timestamp": timezone.localtime(timezone.now()),
            }
        )

    def get_status(self):
        """
        Get the current status from the buffer.
        """
        return self.buffer[-1] if self.buffer else None
