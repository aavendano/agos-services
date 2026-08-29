import uuid
from django.db import models

class MCPClient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="e.g. Claude Desktop, Cursor, Antigravity Agent")
    token = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    is_active = models.BooleanField(default=True)
    rate_limit_rpm = models.PositiveIntegerField(default=60, help_text="Requests per minute rate limit")
    description = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mcp_clients"
        ordering = ["-created_at"]
        verbose_name = "MCP Client"
        verbose_name_plural = "MCP Clients"

    def __str__(self):
        return f"{self.name} ({'Active' if self.is_active else 'Disabled'})"

    def has_permission_for_tool(self, tool_name: str) -> bool:
        if not self.is_active:
            return False
        return self.permissions.filter(tool_name=tool_name, allowed=True).exists()


class ToolPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client = models.ForeignKey(MCPClient, on_delete=models.CASCADE, related_name="permissions")
    tool_name = models.CharField(max_length=100, db_index=True, help_text="e.g. get_products, create_order")
    allowed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "mcp_tool_permissions"
        unique_together = ("client", "tool_name")
        ordering = ["client", "tool_name"]
        verbose_name = "Tool Permission"
        verbose_name_plural = "Tool Permissions"

    def __str__(self):
        return f"{self.client.name} -> {self.tool_name}: {'ALLOWED' if self.allowed else 'DENIED'}"
