from django.contrib import admin
from .models import AuditLog

class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'role', 'action', 'target_model', 'target_id')
    list_filter = ('role', 'action', 'target_model')
    search_fields = ('user__username', 'target_model', 'comments')
    readonly_fields = ('user', 'role', 'action', 'target_model', 'target_id', 'timestamp', 'comments')

    def has_add_permission(self, request): return False
    def has_delete_permission(self, request, obj=None): return False

admin.site.register(AuditLog, AuditLogAdmin)
