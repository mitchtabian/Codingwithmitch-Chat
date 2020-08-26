from django.contrib import admin

from notification.models import Notification

class NotificationAdmin(admin.ModelAdmin):
    list_filter = ['content_type', ]
    list_display = ['target', 'content_type', ]
    search_fields = ['target', 'content_type',]
    readonly_fields = []

    class Meta:
        model = Notification


admin.site.register(Notification, NotificationAdmin)
