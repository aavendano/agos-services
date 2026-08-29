from django.contrib import admin
from .models import MCPClient, ToolPermission

class ToolPermissionInline(admin.TabularInline):
    model = ToolPermission
    extra = 1

@admin.register(MCPClient)
class MCPClientAdmin(admin.ModelAdmin):
    list_display = ("name", "token", "is_active", "rate_limit_rpm", "created_at")
    list_filter = ("is_active", "created_at")
    search_fields = ("name", "token")
    readonly_fields = ("id", "token", "created_at", "updated_at")
    inlines = [ToolPermissionInline]

@admin.register(ToolPermission)
class ToolPermissionAdmin(admin.ModelAdmin):
    list_display = ("client", "tool_name", "allowed", "updated_at")
    list_filter = ("allowed", "tool_name", "client")
    search_fields = ("tool_name", "client__name")
