from django.utils import timezone
from administrator.models import WorkDeskStatus, DeskStatusEnum, WorkDesk
from django.utils import timezone
from uuid import uuid4


class StatusBuffer:
    PING_CHUNK = 20
    LAST_CLEARED_BUFFER = timezone.now()
    CLEAR_BUFFER_INTERVAL = 60 * 5  # 5 minutes

    def __init__(self):
        self.buffer = []
        self.ping_count = 0
        self.all_desk_instances_map = {
            desk.desk_number: desk for desk in WorkDesk.objects.all()
        }

    def add_status(self, desk_no, status_enum):
        self.ping_count += 1
        """
        adds status to the buffer along with the timestamp and desk number.
        if the buffer exceeds the BUFFER_SIZE, it stores the buffer in the database in batches.
        And then clears the buffer.
        """
        if (timezone.now() - self.LAST_CLEARED_BUFFER).seconds > self.CLEAR_BUFFER_INTERVAL:
            print("Clearing buffer after 5 minutes.")
            self.buffer = []
            self.ping_count = 0
            self.LAST_CLEARED_BUFFER = timezone.now()

        if self.ping_count >= self.PING_CHUNK:
            print("Buffer size exceeded, saving to database. (Using Bulk create)")
            print(self.buffer, self.ping_count)
            # print(self.all_desk_instances_map.get(data["workdesk"])

            # update or create the statuses in the database
            for data in self.buffer:
                print(self.all_desk_instances_map.get(data["workdesk_no"]))
                print(self.all_desk_instances_map)
                print(data["workdesk_no"])

                try:
                    WorkDeskStatus.objects.update_or_create(
                        unique_id=data["unique_id"],
                        defaults={
                            "workdesk": self.all_desk_instances_map.get(
                                data["workdesk_no"]
                            ),
                            "status": DeskStatusEnum(data["status_enum"]).name,
                            "created_at": data["start_time"],
                            "updated_at": timezone.localtime(timezone.now()),
                        },
                    )
                    print("saved")
                except Exception as e:
                    print(
                        f"**************************Error saving status to database: {e}"
                    )

            # Clear the buffer after saving to the database
            self.ping_count = 0

        # avoid duplicate statues
        if self.buffer or len(self.buffer) > 0:
            # search for the last status in the buffer with the same desk number and status
            for status in reversed(self.buffer):
                if (
                    status["workdesk_no"] == str(desk_no)
                    and status["status_enum"] == status_enum
                ):
                    print("Found duplicate status, updating timestamp.")
                    status["timestamp"] = timezone.localtime(timezone.now())
                    return

        self.buffer.append(
            {
                "unique_id": uuid4(),
                "workdesk_no": str(desk_no),
                "status_enum": status_enum,
                "start_time": timezone.localtime(timezone.now()),
                "timestamp": timezone.localtime(timezone.now()),
            }
        )

    def get_status(self):
        """
        Get the current status from the buffer.
        """
        return self.buffer[-1] if self.buffer else None
