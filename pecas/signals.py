from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Peca
from atividades.models import Atividade


@receiver(post_save, sender=Peca)
def criar_atividade_para_peca(sender, instance, created, **kwargs):
    """
    Cria automaticamente uma atividade quando uma nova peça é cadastrada.
    """
    if created:  # Apenas para novas peças (não para atualizações)
        # Cria uma atividade para produção da peça
        Atividade.objects.create(
            titulo=f"Produzir peça {instance.codigo}",
            descricao=f"Produção da peça: {instance.descricao or 'Sem descrição'}\n"
            f"Cliente: {instance.cliente.nome}\n"
            f"Quantidade: {instance.quantidade}\n"
            f"Data de entrega: {instance.data_entrega or 'Não definida'}",
            peca=instance,
            status=Atividade.StatusChoices.NA_FILA,
            prioridade=1,  # Prioridade média
            metadata={
                "tipo": "producao_peca",
                "peca_codigo": instance.codigo,
                "cliente_nome": instance.cliente.nome,
                "quantidade": instance.quantidade,
                "data_entrega": str(instance.data_entrega) if instance.data_entrega else None,
            },
        )
