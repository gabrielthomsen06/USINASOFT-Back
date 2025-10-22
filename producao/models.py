import uuid
from django.db import models
from django.conf import settings


class OrdemProducao(models.Model):
    """
    Modelo que representa uma ordem de produção (OP).
    """

    class StatusChoices(models.TextChoices):
        ABERTA = "aberta", "Aberta"
        EM_ANDAMENTO = "em_andamento", "Em Andamento"
        PAUSADA = "pausada", "Pausada"
        CONCLUIDA = "concluida", "Concluída"
        CANCELADA = "cancelada", "Cancelada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    numero = models.CharField(max_length=50, unique=True, verbose_name="Número da OP")
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="ops_criadas",
        verbose_name="Criado por",
    )
    data_criacao = models.DateTimeField(auto_now_add=True, verbose_name="Data de Criação")
    data_inicio_prevista = models.DateField(
        blank=True, null=True, verbose_name="Data Início Prevista"
    )
    data_fim_prevista = models.DateField(blank=True, null=True, verbose_name="Data Fim Prevista")
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
            models.Index(fields=["numero"]),
            models.Index(fields=["status"]),
            models.Index(fields=["criado_por", "status"]),
            # Índice para filtros de período + status (usado pelos indicadores)
            models.Index(fields=["data_fim_prevista", "status"]),
        ]

    def __str__(self):
        return f"OP {self.numero} - {self.get_status_display()}"


class OrdemProducaoItem(models.Model):
    """
    Modelo que representa um item dentro de uma ordem de produção.
    """

    class StatusChoices(models.TextChoices):
        PENDENTE = "pendente", "Pendente"
        EM_PRODUCAO = "em_producao", "Em Produção"
        PAUSADO = "pausado", "Pausado"
        CONCLUIDO = "concluido", "Concluído"
        CANCELADO = "cancelado", "Cancelado"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordem = models.ForeignKey(
        OrdemProducao,
        on_delete=models.CASCADE,
        related_name="itens",
        verbose_name="Ordem de Produção",
    )
    peca = models.ForeignKey(
        "pecas.Peca", on_delete=models.PROTECT, related_name="op_itens", verbose_name="Peça"
    )
    quantidade = models.IntegerField(verbose_name="Quantidade")
    quantidade_produzida = models.IntegerField(default=0, verbose_name="Quantidade Produzida")
    status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDENTE,
        verbose_name="Status",
    )
    lote = models.CharField(max_length=100, blank=True, null=True, verbose_name="Lote")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Item de Ordem de Produção"
        verbose_name_plural = "Itens de Ordens de Produção"
        ordering = ["ordem", "-created_at"]
        indexes = [
            models.Index(fields=["ordem", "status"]),
            models.Index(fields=["peca"]),
        ]

    def __str__(self):
        return f"{self.ordem.numero} - {self.peca.codigo}"

    def clean(self):
        """Validação customizada."""
        from django.core.exceptions import ValidationError

        if self.quantidade and self.quantidade <= 0:
            raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})

        if self.quantidade_produzida < 0:
            raise ValidationError(
                {"quantidade_produzida": "A quantidade produzida não pode ser negativa."}
            )

        if self.quantidade and self.quantidade_produzida > self.quantidade:
            raise ValidationError(
                {
                    "quantidade_produzida": "A quantidade produzida não pode ser maior que a quantidade solicitada."
                }
            )

    @property
    def percentual_concluido(self):
        """Retorna o percentual de conclusão do item."""
        if self.quantidade > 0:
            return (self.quantidade_produzida / self.quantidade) * 100
        return 0
