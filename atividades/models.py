import uuid
from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class Atividade(models.Model):
    """
    Modelo que representa uma atividade/tarefa no sistema Kanban.
    """

    class StatusChoices(models.TextChoices):
        NA_FILA = "na_fila", "Na Fila"
        EM_ANDAMENTO = "em_andamento", "Em Andamento"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    titulo = models.CharField(max_length=200, verbose_name="Título")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atividades",
        verbose_name="Responsável",
    )
    ordem = models.ForeignKey(
        "producao.OrdemProducao",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atividades",
        verbose_name="Ordem de Produção",
    )
    ordem_item = models.ForeignKey(
        "producao.OrdemProducaoItem",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atividades",
        verbose_name="Item de OP",
    )
    peca = models.ForeignKey(
        "pecas.Peca",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="atividades",
        verbose_name="Peça",
    )
    status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices,
        default=StatusChoices.NA_FILA,
        verbose_name="Status",
    )
    prioridade = models.IntegerField(default=0, verbose_name="Prioridade")
    data_inicio = models.DateTimeField(blank=True, null=True, verbose_name="Data de Início")
    data_fim = models.DateTimeField(blank=True, null=True, verbose_name="Data de Fim")
    posicao = models.IntegerField(blank=True, null=True, verbose_name="Posição")
    metadata = models.JSONField(blank=True, null=True, verbose_name="Metadados")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Atividade"
        verbose_name_plural = "Atividades"
        ordering = ["posicao", "-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["responsavel", "status"]),
            models.Index(fields=["ordem", "status"]),
            models.Index(fields=["prioridade"]),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.get_status_display()}"


class Comentario(models.Model):
    """
    Modelo que representa comentários em atividades.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    atividade = models.ForeignKey(
        Atividade, on_delete=models.CASCADE, related_name="comentarios", verbose_name="Atividade"
    )
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="comentarios",
        verbose_name="Autor",
    )
    texto = models.TextField(verbose_name="Texto")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Comentário"
        verbose_name_plural = "Comentários"
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["atividade", "created_at"]),
        ]

    def __str__(self):
        return f"Comentário de {self.autor} em {self.atividade.titulo}"


class Anexo(models.Model):
    """
    Modelo que representa anexos de arquivos.
    Pode ser anexado a múltiplos tipos de objetos usando GenericForeignKey.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # GenericForeignKey para flexibilidade
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.UUIDField()
    content_object = GenericForeignKey("content_type", "object_id")

    arquivo_path = models.CharField(max_length=512, verbose_name="Caminho do Arquivo")
    nome_original = models.CharField(
        max_length=255, blank=True, null=True, verbose_name="Nome Original"
    )
    mime_type = models.CharField(max_length=100, blank=True, null=True, verbose_name="Tipo MIME")
    tamanho = models.IntegerField(blank=True, null=True, verbose_name="Tamanho (bytes)")
    metadata = models.JSONField(blank=True, null=True, verbose_name="Metadados")
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="anexos",
        verbose_name="Criado por",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")

    class Meta:
        verbose_name = "Anexo"
        verbose_name_plural = "Anexos"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["criado_por"]),
        ]

    def __str__(self):
        return f'{self.nome_original or "Anexo"} - {self.created_at}'
