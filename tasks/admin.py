from django.contrib import admin
from .models import Task,Project

# Register your models here.
@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['id','name','owner','task_count','created_at']
    list_filter = ['owner']
    search_fields = ['name','description']
    
    def task_count(self,obj):
        return obj.task.count()
    
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['id','title','project','status','priority','deadline']
    list_filter = ['status', 'priority']
    search_fields = ['title','description']
    
    