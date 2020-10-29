from django.contrib import admin

from friend.models import FriendList, FriendRequest


class FriendListAdmin(admin.ModelAdmin):
    list_filter = ['user']
    list_display = ['user']
    search_fields = ['user']
    readonly_fields = ['user',]

    class Meta:
        model = FriendList


admin.site.register(FriendList, FriendListAdmin)


class FriendRequestAdmin(admin.ModelAdmin):
    list_filter = ['sender', 'receiver']
    list_display = ['sender', 'receiver',]
    search_fields = ['sender__username', 'receiver__username']
    readonly_fields = ['id',]

    class Meta:
        model = FriendRequest


admin.site.register(FriendRequest, FriendRequestAdmin)












