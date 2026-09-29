from django.db import models
from django.utils import timezone

class JobHistory(models.Model):
    JOB_TYPES = (
        ('Sqoop', 'Sqoop Import'),
        ('MapReduce', 'MapReduce Analysis'),
    )
    
    STATUS_CHOICES = (
        ('Running', 'Đang chạy'),
        ('Completed', 'Hoàn thành'),
        ('Failed', 'Thất bại'),
    )

    job_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    table_name = models.CharField(max_length=100, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Running')
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(null=True, blank=True)
    logs = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.job_id} - {self.name}"

    @property
    def duration(self):
        if self.start_time and self.end_time:
            diff = self.end_time - self.start_time
            total_seconds = int(diff.total_seconds())
            minutes, seconds = divmod(total_seconds, 60)
            if minutes > 0:
                return f"{minutes}m {seconds}s"
            return f"{seconds}s"
        return "In Progress"

