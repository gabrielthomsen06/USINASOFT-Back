from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Atividade, Comentario, Anexo
from .serializers import AtividadeSerializer, ComentarioSerializer, AnexoSerializer


class AtividadeViewSet(viewsets.ModelViewSet):
    queryset = (
        Atividade.objects.select_related("responsavel", "ordem", "ordem_item", "peca")
        .all()
        .order_by("-created_at")
    )
    serializer_class = AtividadeSerializer
    permission_classes = [AllowAny]


class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.select_related("atividade", "autor").all().order_by("created_at")
    serializer_class = ComentarioSerializer
    permission_classes = [AllowAny]


class AnexoViewSet(viewsets.ModelViewSet):
    queryset = (
        Anexo.objects.select_related("criado_por", "content_type").all().order_by("-created_at")
    )
    serializer_class = AnexoSerializer
    permission_classes = [AllowAny]
