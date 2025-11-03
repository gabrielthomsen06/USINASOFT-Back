from rest_framework import serializers
from .models import Cliente, Peca
from producao.models import OrdemProducao


class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ["id", "nome", "contato", "email", "endereco", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class PecaSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.ReadOnlyField(source="cliente.nome")
    ordem_producao_codigo = serializers.CharField(write_only=True)
    op_codigo = serializers.ReadOnlyField(source="ordem_producao.codigo")
    op_status = serializers.ReadOnlyField(source="ordem_producao.status")

    class Meta:
        model = Peca
        fields = [
            "id",
            "ordem_producao",
            "ordem_producao_codigo",
            "op_codigo",
            "op_status",
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
        read_only_fields = ["id", "ordem_producao", "created_at", "updated_at"]

    def create(self, validated_data):
        """
        Cria a peça e automaticamente cria ou associa a uma OP baseada no código da NF.
        """
        ordem_producao_codigo = validated_data.pop("ordem_producao_codigo")
        cliente = validated_data.get("cliente")

        # Buscar ou criar OP com o código informado
        ordem_producao, created = OrdemProducao.objects.get_or_create(
            codigo=ordem_producao_codigo,
            defaults={
                "cliente": cliente,
                "status": "aberta",
            },
        )

        # Se a OP já existia mas com cliente diferente, manter o cliente original
        # (isso evita inconsistências caso múltiplos clientes usem o mesmo número de NF)

        # Associar a peça à OP
        validated_data["ordem_producao"] = ordem_producao

        return super().create(validated_data)
