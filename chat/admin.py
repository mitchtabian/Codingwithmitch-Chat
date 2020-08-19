from django.contrib import admin
from django.db import models

from chat.models import Room, RoomChatMessage

class RoomAdmin(admin.ModelAdmin):
    list_filter = ['id', 'title', 'staff_only', ]
    list_display = ['id', 'title', 'staff_only']
    search_fields = ['id', 'title']
    readonly_fields = ['id','connected_users',]

    class Meta:
        model = Room


admin.site.register(Room, RoomAdmin)



# class ApproxCountPgQuerySet(models.query.QuerySet):
#   """approximate unconstrained count(*) with reltuples from pg_class"""

#   def count(self):
#       if self._result_cache is not None and not self._iter:
#           return len(self._result_cache)

#       if hasattr(connections[self.db].client.connection, 'pg_version'):
#           query = self.query
#           if (not query.where and query.high_mark is None and query.low_mark == 0 and
#               not query.select and not query.group_by and not query.having and not query.distinct):
#               # If query has no constraints, we would be simply doing
#               # "SELECT COUNT(*) FROM foo". Monkey patch so the we get an approximation instead.
#               parts = [p.strip('"') for p in self.model._meta.db_table.split('.')]
#               cursor = connections[self.db].cursor()
#               if len(parts) == 1:
#                   cursor.execute("select reltuples::bigint FROM pg_class WHERE relname = %s", parts)
#               else:
#                   cursor.execute("select reltuples::bigint FROM pg_class c JOIN pg_namespace n on (c.relnamespace = n.oid) WHERE n.nspname = %s AND c.relname = %s", parts)
#           return cursor.fetchall()[0][0]
#       return self.query.get_count(using=self.db)

from django.core.paginator import Paginator
from django.core.cache import cache

# Resource: http://masnun.rocks/2017/03/20/django-admin-expensive-count-all-queries/
class CachingPaginator(Paginator):
    def _get_count(self):

        if not hasattr(self, "_count"):
            self._count = None

        if self._count is None:
            try:
                key = "adm:{0}:count".format(hash(self.object_list.query.__str__()))
                self._count = cache.get(key, -1)
                if self._count == -1:
                    self._count = super().count
                    cache.set(key, self._count, 3600)

            except:
                self._count = len(self.object_list)
        return self._count

    count = property(_get_count)


class RoomChatMessageAdmin(admin.ModelAdmin):
    list_filter = ['room',  'user', "timestamp"]
    list_display = ['room',  'user', 'content',"timestamp"]
    search_fields = ['room__title', 'user__username','content']
    readonly_fields = ['id', "user", "room", "timestamp"]

    show_full_result_count = False
    paginator = CachingPaginator

    class Meta:
        model = RoomChatMessage


admin.site.register(RoomChatMessage, RoomChatMessageAdmin)














