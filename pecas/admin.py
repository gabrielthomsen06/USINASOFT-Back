from django.contrib import admin
from .models import Cliente, Peca


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Admin para o modelo Cliente."""

    list_display = ("nome", "contato", "email", "created_at")
    list_filter = ("created_at",)
    search_fields = ("nome", "email", "contato")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("nome",)


@admin.register(Peca)
class PecaAdmin(admin.ModelAdmin):
    """Admin para o modelo Peca."""

    list_display = (
        "codigo",
        "descricao",
        "cliente",
        "quantidade",
        "status",
        "data_entrega",
        "created_at",
    )
    list_filter = ("status", "created_at", "data_entrega", "cliente")
    search_fields = ("codigo", "descricao", "pedido", "cliente__nome")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)

    fieldsets = (
        ("Informações Básicas", {"fields": ("cliente", "codigo", "descricao", "pedido")}),
        ("Produção", {"fields": ("quantidade", "data_entrega", "status")}),
        ("Metadados", {"fields": ("metadata",), "classes": ("collapse",)}),
        ("Datas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
