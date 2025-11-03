from rest_framework import serializers
from .models import OrdemProducao


class OrdemProducaoSerializer(serializers.ModelSerializer):
    criado_por_email = serializers.ReadOnlyField(source="criado_por.email")
    cliente_nome = serializers.ReadOnlyField(source="cliente.nome")
    total_pecas = serializers.ReadOnlyField()
    pecas_concluidas = serializers.ReadOnlyField()
    percentual_conclusao = serializers.ReadOnlyField()

    class Meta:
        model = OrdemProducao
        fields = [
            "id",
            "codigo",
            "cliente",
            "cliente_nome",
            "criado_por",
            "criado_por_email",
            "status",
            "observacoes",
            "total_pecas",
            "pecas_concluidas",
            "percentual_conclusao",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "total_pecas",
            "pecas_concluidas",
            "percentual_conclusao",
            "created_at",
            "updated_at",
        ]
