from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from apps.task.resource import TaskResource


from .models import Profile, TaskTemplate, Task, TaskCategory

admin.site.register(Profile)
admin.site.register(Task)
admin.site.register(TaskCategory)

@admin.register(TaskTemplate)
class TaskTemplateAdmin(ImportExportModelAdmin):
    resource_class = TaskResource
    
    