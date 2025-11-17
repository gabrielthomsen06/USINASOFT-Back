import uuid
from django.db import models
from django.conf import settings


class OrdemProducao(models.Model):
    """
    Modelo que representa uma ordem de produção (OP).
    O código da OP corresponde ao número da nota fiscal física.
    """

    class StatusChoices(models.TextChoices):
        ABERTA = "aberta", "Aberta"
        EM_ANDAMENTO = "em_andamento", "Em Andamento"
        CONCLUIDA = "concluida", "Concluída"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(
        max_length=50, unique=True, verbose_name="Código da OP (Número da NF)"
    )
    cliente = models.ForeignKey(
        "pecas.Cliente",
        on_delete=models.PROTECT,
        related_name="ordens_producao",
        verbose_name="Cliente",
    )
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ops_criadas",
        verbose_name="Criado por",
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ops_responsavel",
        verbose_name="Responsável",
    )
    status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices,
        default=StatusChoices.ABERTA,
        verbose_name="Status",
    )
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Ordem de Produção"
        verbose_name_plural = "Ordens de Produção"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["status"]),
            models.Index(fields=["cliente"]),
            models.Index(fields=["created_at", "status"]),
        ]

    def __str__(self):
        return f"OP {self.codigo} - {self.get_status_display()}"

    @property
    def total_pecas(self):
        """Retorna o total de peças nesta OP."""
        return self.pecas.count()

    @property
    def pecas_concluidas(self):
        """Retorna o número de peças concluídas."""
        return self.pecas.filter(status="concluida").count()

    @property
    def percentual_conclusao(self):
        """Calcula o percentual de conclusão baseado nas peças."""
        total = self.total_pecas
        if total == 0:
            return 0
        return round((self.pecas_concluidas / total) * 100, 2)

    def verificar_e_atualizar_status(self):
        """
        Verifica o estado das peças e atualiza o status da OP automaticamente:
        - Se todas as peças estão concluídas -> status = 'concluida'
        - Se pelo menos uma peça está em andamento -> status = 'em_andamento'
        - Caso contrário -> mantém status atual
        """
        total = self.total_pecas

        # Se não há peças, não faz nada
        if total == 0:
            return False

        concluidas = self.pecas_concluidas
        em_andamento = self.pecas.filter(status="em_andamento").count()

        status_anterior = self.status

        # Se todas as peças estão concluídas
        if concluidas == total:
            self.status = self.StatusChoices.CONCLUIDA
        # Se pelo menos uma peça está em andamento
        elif em_andamento > 0:
            self.status = self.StatusChoices.EM_ANDAMENTO

        # Salvar apenas se o status mudou
        if self.status != status_anterior:
            self.save(update_fields=["status", "updated_at"])
            return True

        return False
