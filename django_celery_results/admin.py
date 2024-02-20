"""Result Task Admin interface."""

from django.conf import settings
from django.contrib import admin
from django.db.models import F
from django.utils.translation import gettext_lazy as _

try:
    ALLOW_EDITS = settings.DJANGO_CELERY_RESULTS['ALLOW_EDITS']
except (AttributeError, KeyError):
    ALLOW_EDITS = False
    pass

from .models import GroupResult, TaskResult


class TaskResultAdmin(admin.ModelAdmin):
    """Admin-interface for results of tasks."""

    model = TaskResult
    date_hierarchy = 'date_done'
    list_display = ('task_id', 'task_name', 'date_created', 'date_done',
                    'get_processing_time', 'status', 'worker', 
                    'periodic_task_name')
    list_filter = ('status', 'date_done', 'periodic_task_name', 'task_name',
                   'worker')
    readonly_fields = ('date_created', 'date_done', 'result', 'meta')
    search_fields = ('task_name', 'task_id', 'status', 'task_args',
                     'task_kwargs')
    fieldsets = (
        (None, {
            'fields': (
                'task_id',
                'task_name',
                'periodic_task_name',
                'status',
                'worker',
                'content_type',
                'content_encoding',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Parameters'), {
            'fields': (
                'task_args',
                'task_kwargs',
            ),
            'classes': ('extrapretty', 'wide')
        }),
        (_('Result'), {
            'fields': (
                'result',
                'date_created',
                'date_done',
                'traceback',
                'meta',
            ),
            'classes': ('extrapretty', 'wide')
        }),
    )

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _processing_time=F("date_done") - F("date_created"),
        )
        return queryset
    
    def get_readonly_fields(self, request, obj=None):
        if ALLOW_EDITS:
            return self.readonly_fields
        else:
            return list({
                field.name for field in self.opts.local_fields
            })

    def get_processing_time(self, obj):
        minutes = int(obj._processing_time.seconds / 60)
        seconds = int(obj._processing_time.seconds % 60)
        return f"{minutes}:{seconds:02d} mins"

    get_processing_time.short_description = "Processing time"
    get_processing_time.admin_order_field = "_processing_time"

admin.site.register(TaskResult, TaskResultAdmin)


class GroupResultAdmin(admin.ModelAdmin):
    """Admin-interface for results  of grouped tasks."""

    model = GroupResult
    date_hierarchy = 'date_done'
    list_display = ('group_id', 'date_done')
    list_filter = ('date_done',)
    readonly_fields = ('date_created', 'date_done', 'result')
    search_fields = ('group_id',)


admin.site.register(GroupResult, GroupResultAdmin)
