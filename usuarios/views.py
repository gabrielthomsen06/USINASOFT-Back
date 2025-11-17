from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import Usuario, LogAcao
from .serializers import UsuarioSerializer, LogAcaoSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all().order_by("-created_at")
    serializer_class = UsuarioSerializer
    permission_classes = [AllowAny]  # Permite criação sem auth para registro inicial


class LogAcaoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = LogAcao.objects.all().order_by("-created_at")
    serializer_class = LogAcaoSerializer
    permission_classes = [AllowAny]


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Retorna os dados do usuário logado."""
    serializer = UsuarioSerializer(request.user)
    return Response(serializer.data)
