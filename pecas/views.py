from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Cliente, Peca
from .serializers import ClienteSerializer, PecaSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by("nome")
    serializer_class = ClienteSerializer
    permission_classes = [AllowAny]


class PecaViewSet(viewsets.ModelViewSet):
    queryset = Peca.objects.select_related("cliente").all().order_by("-created_at")
    serializer_class = PecaSerializer
    permission_classes = [AllowAny]
