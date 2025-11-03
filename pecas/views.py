from rest_framework import viewsets
from .models import Cliente, Peca
from .serializers import ClienteSerializer, PecaSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by("nome")
    serializer_class = ClienteSerializer


class PecaViewSet(viewsets.ModelViewSet):
    queryset = Peca.objects.select_related("cliente").all().order_by("-created_at")
    serializer_class = PecaSerializer
