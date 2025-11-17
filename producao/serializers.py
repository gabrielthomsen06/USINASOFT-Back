from rest_framework import serializers
from .models import OrdemProducao


class OrdemProducaoSerializer(serializers.ModelSerializer):
    criado_por_email = serializers.ReadOnlyField(source="criado_por.email")
    criado_por_nome = serializers.ReadOnlyField(source="criado_por.get_full_name")
    responsavel_email = serializers.ReadOnlyField(source="responsavel.email")
    responsavel_nome = serializers.ReadOnlyField(source="responsavel.get_full_name")
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
            "criado_por_nome",
            "responsavel",
            "responsavel_email",
            "responsavel_nome",
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
            "criado_por_email",
            "criado_por_nome",
            "responsavel_email",
            "responsavel_nome",
            "total_pecas",
            "pecas_concluidas",
            "percentual_conclusao",
            "created_at",
            "updated_at",
        ]
