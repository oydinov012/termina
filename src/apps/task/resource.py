from import_export import resources, fields
from import_export.widgets import ManyToManyWidget
from apps.task.models import TaskCategory, TaskTemplate

class TaskResource(resources.ModelResource):
    # 'categories' maydoni uchun ManyToManyWidget dan foydalanamiz
    categories = fields.Field(
        column_name='categories',
        attribute='categories',
        widget=ManyToManyWidget(TaskCategory, field='name', separator=',') 
    )

    class Meta:
        model = TaskTemplate
        # Maydonlar ro'yxati (fields)
        fields = (
            'id', 'title', 'description', 'target_structure', 'command', 
            'expected_output', 'level', 'type', 'difficulty', 'categories', 
            'xp', 'is_active'
        )
        # Import qilinganda eski ma'lumotlarni yangilash uchun id kerak bo'lishi mumkin
        import_id_fields = ('title',) 