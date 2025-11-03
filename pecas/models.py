import uuid
from django.db import models


class Cliente(models.Model):
    """
    Modelo que representa um cliente do sistema.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    nome = models.CharField(max_length=200, verbose_name="Nome")
    contato = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contato")
    email = models.EmailField(blank=True, null=True, verbose_name="Email")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nome"]
        indexes = [
            models.Index(fields=["nome"]),
        ]

    def __str__(self):
        return self.nome


class Peca(models.Model):
    """
    Modelo que representa uma peça/produto a ser produzido.
    """

    class StatusChoices(models.TextChoices):
        EM_FILA = "em_fila", "Em Fila"
        EM_ANDAMENTO = "em_andamento", "Em Andamento"
        PAUSADA = "pausada", "Pausada"
        CONCLUIDA = "concluida", "Concluída"
        CANCELADA = "cancelada", "Cancelada"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ordem_producao = models.ForeignKey(
        "producao.OrdemProducao",
        on_delete=models.CASCADE,
        related_name="pecas",
        verbose_name="Ordem de Produção",
    )
    cliente = models.ForeignKey(
        Cliente, on_delete=models.PROTECT, related_name="pecas", verbose_name="Cliente"
    )
    codigo = models.CharField(max_length=100, unique=True, verbose_name="Código")
    descricao = models.TextField(blank=True, null=True, verbose_name="Descrição")
    pedido = models.CharField(
        max_length=100, blank=True, null=True, verbose_name="Número do Pedido"
    )
    quantidade = models.IntegerField(verbose_name="Quantidade")
    data_entrega = models.DateField(blank=True, null=True, verbose_name="Data de Entrega")
    status = models.CharField(
        max_length=30,
        choices=StatusChoices.choices,
        default=StatusChoices.EM_FILA,
        verbose_name="Status",
    )
    metadata = models.JSONField(blank=True, null=True, verbose_name="Metadados")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Peça"
        verbose_name_plural = "Peças"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["codigo"]),
            models.Index(fields=["status"]),
            models.Index(fields=["data_entrega"]),
            models.Index(fields=["cliente", "status"]),
            models.Index(fields=["ordem_producao"]),
        ]

    def __str__(self):
        return f'{self.codigo} - {self.descricao or "Sem descrição"}'

    def clean(self):
        """Validação customizada."""
        from django.core.exceptions import ValidationError

        if self.quantidade and self.quantidade <= 0:
            raise ValidationError({"quantidade": "A quantidade deve ser maior que zero."})

        if self.data_entrega and self.created_at:
            if self.data_entrega < self.created_at.date():
                raise ValidationError(
                    {"data_entrega": "A data de entrega não pode ser anterior à data de criação."}
                )
