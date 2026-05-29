from celery import shared_task
from django.utils import timezone


@shared_task
def check_overdue_task():
    from .models import Task
    tasks = Task.objects.filter(
        deadline__lt = timezone.now().date(),
        status__in = ['todo','in_progress']
    )
    
    count = tasks.count()
    for task in tasks:
        print(f"OVERDUE: '{task.title}', in project '{task.project.name}'")
        
    return f"Checked overdue tasks: {count} found"