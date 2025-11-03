from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
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
