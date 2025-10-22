from rest_framework import serializers
from .models import Atividade, Comentario, Anexo
from django.contrib.contenttypes.models import ContentType


class AtividadeSerializer(serializers.ModelSerializer):
    responsavel_email = serializers.ReadOnlyField(source="responsavel.email")
    ordem_numero = serializers.ReadOnlyField(source="ordem.numero")
    peca_codigo = serializers.ReadOnlyField(source="peca.codigo")

    class Meta:
        model = Atividade
        fields = [
            "id",
            "titulo",
            "descricao",
            "responsavel",
            "responsavel_email",
            "ordem",
            "ordem_numero",
            "ordem_item",
            "peca",
            "peca_codigo",
            "status",
            "prioridade",
            "data_inicio",
            "data_fim",
            "posicao",
            "metadata",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class ComentarioSerializer(serializers.ModelSerializer):
    autor_email = serializers.ReadOnlyField(source="autor.email")

    class Meta:
        model = Comentario
        fields = ["id", "atividade", "autor", "autor_email", "texto", "created_at"]
        read_only_fields = ["id", "created_at"]


class ContentTypeField(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        return ContentType.objects.all()


class AnexoSerializer(serializers.ModelSerializer):
    criado_por_email = serializers.ReadOnlyField(source="criado_por.email")
    content_type = ContentTypeField()

    class Meta:
        model = Anexo
        fields = [
            "id",
            "content_type",
            "object_id",
            "arquivo_path",
            "nome_original",
            "mime_type",
            "tamanho",
            "metadata",
            "criado_por",
            "criado_por_email",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]
