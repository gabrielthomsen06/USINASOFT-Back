from rest_framework import serializers
from .models import OrdemProducao, OrdemProducaoItem


class OrdemProducaoSerializer(serializers.ModelSerializer):
    criado_por_email = serializers.ReadOnlyField(source="criado_por.email")

    class Meta:
        model = OrdemProducao
        fields = [
            "id",
            "numero",
            "criado_por",
            "criado_por_email",
            "data_criacao",
            "data_inicio_prevista",
            "data_fim_prevista",
            "status",
            "observacoes",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "data_criacao", "created_at", "updated_at"]


class OrdemProducaoItemSerializer(serializers.ModelSerializer):
    ordem_numero = serializers.ReadOnlyField(source="ordem.numero")
    peca_codigo = serializers.ReadOnlyField(source="peca.codigo")
    percentual_concluido = serializers.ReadOnlyField()

    class Meta:
        model = OrdemProducaoItem
        fields = [
            "id",
            "ordem",
            "ordem_numero",
            "peca",
            "peca_codigo",
            "quantidade",
            "quantidade_produzida",
            "percentual_concluido",
            "status",
            "lote",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "percentual_concluido", "created_at", "updated_at"]
