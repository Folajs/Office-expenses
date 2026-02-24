from django.contrib import admin
from .models import User, Department
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (('Custom Fields', {'fields': ('role', 'department')}),)

admin.site.register(User, UserAdmin)
admin.site.register(Department)
