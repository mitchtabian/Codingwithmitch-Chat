from django.contrib import admin

from chat.models import Room

class RoomAdmin(admin.ModelAdmin):
    list_filter = ['id', 'title', 'staff_only']
    list_display = ['id', 'title', 'staff_only']
    search_fields = ['id', 'title']
    readonly_fields = ['id']

    class Meta:
        model = Room


admin.site.register(Room, RoomAdmin)