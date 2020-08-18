from django.contrib import admin

from chat.models import Room, RoomChatMessage

class RoomAdmin(admin.ModelAdmin):
    list_filter = ['id', 'title', 'staff_only']
    list_display = ['id', 'title', 'staff_only']
    search_fields = ['id', 'title']
    readonly_fields = ['id']

    class Meta:
        model = Room


admin.site.register(Room, RoomAdmin)




class RoomChatMessageAdmin(admin.ModelAdmin):
    list_filter = ['room',  'user', 'content',"timestamp"]
    list_display = ['room',  'user', 'content',"timestamp"]
    search_fields = ['room__title', 'user__username','content']
    readonly_fields = ['id', "user", "room", "timestamp"]

    class Meta:
        model = RoomChatMessage


admin.site.register(RoomChatMessage, RoomChatMessageAdmin)














