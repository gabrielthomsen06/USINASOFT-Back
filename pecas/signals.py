from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Peca


@receiver(post_save, sender=Peca)
def atualizar_status_op_ao_salvar_peca(sender, instance, created, **kwargs):
    """
    Signal que atualiza o status da OP quando uma peça é salva.

    Quando uma peça muda de status (especialmente para 'concluida' ou 'em_andamento'),
    verifica se todas as peças da OP estão concluídas e atualiza o status da OP.
    """
    if instance.ordem_producao:
        instance.ordem_producao.verificar_e_atualizar_status()


@receiver(post_delete, sender=Peca)
def atualizar_status_op_ao_deletar_peca(sender, instance, **kwargs):
    """
    Signal que atualiza o status da OP quando uma peça é deletada.

    Recalcula o status da OP após a remoção de uma peça.
    """
    if instance.ordem_producao:
        instance.ordem_producao.verificar_e_atualizar_status()
