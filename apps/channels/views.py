from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MCPClient, ToolPermission
from .serializers import MCPClientSerializer, ToolPermissionSerializer

class MCPClientViewSet(viewsets.ModelViewSet):
    queryset = MCPClient.objects.all().prefetch_related("permissions")
    serializer_class = MCPClientSerializer
    permission_classes = [permissions.IsAdminUser]

    @action(detail=True, methods=["post"])
    def regenerate_token(self, request, pk=None):
        import uuid
        client = self.get_object()
        client.token = uuid.uuid4()
        client.save(update_fields=["token", "updated_at"])
        return Response({"status": "token_regenerated", "token": str(client.token)})

    @action(detail=True, methods=["post"])
    def set_permission(self, request, pk=None):
        client = self.get_object()
        tool_name = request.data.get("tool_name")
        allowed = bool(request.data.get("allowed", True))
        if not tool_name:
            return Response({"error": "tool_name is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        perm, _ = ToolPermission.objects.update_or_create(
            client=client,
            tool_name=tool_name,
            defaults={"allowed": allowed},
        )
        return Response(ToolPermissionSerializer(perm).data)


class ToolPermissionViewSet(viewsets.ModelViewSet):
    queryset = ToolPermission.objects.all().select_related("client")
    serializer_class = ToolPermissionSerializer
    permission_classes = [permissions.IsAdminUser]
