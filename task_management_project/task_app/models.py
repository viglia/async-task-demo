from django.db import models


class Job(models.Model):
    STATUS_CHOICES = [
        ("CR", "Created"),
        ("ST", "Started"),
        ("RS", "Restarted"),
        ("DL", "Deleted"),
        ("CN", "Cancelled"),
        ("EN", "Ended")
    ]

    created_at = models.DateTimeField(auto_now_add=True)
    object_id = models.PositiveIntegerField()
    started_at = models.DateTimeField(blank=True, null=True)
    job_status = models.CharField(
        max_length=2,
        choices=STATUS_CHOICES,
        default="CR"
    )
    sleep_time = models.PositiveIntegerField(blank=True, null=True)
