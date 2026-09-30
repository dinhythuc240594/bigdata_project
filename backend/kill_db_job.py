import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core_api.models import JobHistory
job = JobHistory.objects.filter(job_id='JOB-553597').first()
if job:
    print(f"Found job: {job.job_id} - {job.status}")
    job.status = 'Failed'
    from django.utils import timezone
    job.end_time = timezone.now()
    job.save()
    print("Updated job status to Failed.")
else:
    print("Job not found.")
