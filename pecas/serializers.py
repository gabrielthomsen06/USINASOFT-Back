from rest_framework import serializers
from .models import Cliente, Peca


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nome", "contato", "email", "endereco", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PecaSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.ReadOnlyField(source="cliente.nome")

    class Meta:
        model = Peca
        fields = [
            "id",
            "cliente",
            "cliente_nome",
            "codigo",
            "descricao",
            "pedido",
            "quantidade",
            "data_entrega",
            "status",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
