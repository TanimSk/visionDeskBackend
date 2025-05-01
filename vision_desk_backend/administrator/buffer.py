from django.utils import timezone
from administrator.models import WorkDeskStatus, DeskStatusEnum


class StatusBuffer:
    BUFFER_SIZE = 100

    def __init__(self):
        self.buffer = []

    def add_status(self, desk_no, status_enum):
        """
        adds status to the buffer along with the timestamp and desk number.
        if the buffer exceeds the BUFFER_SIZE, it stores the buffer in the database in batches.
        And then clears the buffer.
        """
        if len(self.buffer) >= self.BUFFER_SIZE:
            print("Buffer size exceeded, saving to database. (Using Bulk create)")
            WorkDeskStatus.objects.bulk_create(
                [
                    WorkDeskStatus(
                        workdesk_id=data["workdesk"],
                        status=DeskStatusEnum(data["status_enum"]).name,
                        created_at=data["timestamp"],
                        updated_at=timezone.localtime(timezone.now()),
                    )
                    for data in self.buffer
                ]
            )
            self.clear_buffer()

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
