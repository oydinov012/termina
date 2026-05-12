from django.contrib import admin

from .models import Profile, TaskTemplate, Task, TaskCategory

admin.site.register(Profile)
admin.site.register(Task)
admin.site.register(TaskCategory)
admin.site.register(TaskTemplate)