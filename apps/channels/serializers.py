from rest_framework import serializers
from .models import MCPClient, ToolPermission

class ToolPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolPermission
        fields = ["id", "client", "tool_name", "allowed", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class MCPClientSerializer(serializers.ModelSerializer):
    permissions = ToolPermissionSerializer(many=True, read_only=True)

    class Meta:
        model = MCPClient
        fields = ["id", "name", "token", "is_active", "rate_limit_rpm", "description", "permissions", "created_at", "updated_at"]
        read_only_fields = ["id", "token", "created_at", "updated_at"]
