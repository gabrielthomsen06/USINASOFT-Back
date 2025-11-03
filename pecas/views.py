from rest_framework import viewsets
from .models import Cliente, Peca
from .serializers import ClienteSerializer, PecaSerializer


class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all().order_by("nome")
    serializer_class = ClienteSerializer


class PecaViewSet(viewsets.ModelViewSet):
    queryset = (
        Peca.objects.select_related("cliente", "ordem_producao").all().order_by("-created_at")
    )
    serializer_class = PecaSerializer

    def get_queryset(self):
        """
        Permite filtrar peças por parâmetros de query:
        - ordem_producao: UUID da OP (ex.: /api/pecas/?ordem_producao=<op.id>)
        - ordem_producao_codigo: código/nota fiscal da OP (ex.: /api/pecas/?ordem_producao_codigo=NF-2024-001)
        """
        qs = super().get_queryset()

        op_id = self.request.query_params.get("ordem_producao")
        op_codigo = self.request.query_params.get("ordem_producao_codigo")

        if op_id:
            qs = qs.filter(ordem_producao_id=op_id)
        if op_codigo:
            qs = qs.filter(ordem_producao__codigo=op_codigo)

        return qs
