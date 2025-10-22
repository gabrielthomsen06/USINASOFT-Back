from django.contrib import admin
from .models import OrdemProducao, OrdemProducaoItem


class OrdemProducaoItemInline(admin.TabularInline):
    """Inline para exibir itens da OP no admin."""

    model = OrdemProducaoItem
    extra = 1
    readonly_fields = ("created_at", "updated_at")


@admin.register(OrdemProducao)
class OrdemProducaoAdmin(admin.ModelAdmin):
    """Admin para o modelo OrdemProducao."""

    list_display = (
        "numero",
        "criado_por",
        "status",
        "data_inicio_prevista",
        "data_fim_prevista",
        "created_at",
    )
    list_filter = ("status", "created_at", "data_inicio_prevista")
    search_fields = ("numero", "criado_por__email", "observacoes")
    readonly_fields = ("data_criacao", "created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [OrdemProducaoItemInline]

    fieldsets = (
        ("Informações Básicas", {"fields": ("numero", "criado_por", "status")}),
        ("Datas", {"fields": ("data_criacao", "data_inicio_prevista", "data_fim_prevista")}),
        ("Observações", {"fields": ("observacoes",)}),
        ("Registro", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(OrdemProducaoItem)
class OrdemProducaoItemAdmin(admin.ModelAdmin):
    """Admin para o modelo OrdemProducaoItem."""

    list_display = (
        "ordem",
        "peca",
        "quantidade",
        "quantidade_produzida",
        "percentual_concluido",
        "status",
        "lote",
    )
    list_filter = ("status", "ordem__status", "created_at")
    search_fields = ("ordem__numero", "peca__codigo", "lote")
    readonly_fields = ("created_at", "updated_at", "percentual_concluido")
    ordering = ("-created_at",)

    fieldsets = (
        ("Informações Básicas", {"fields": ("ordem", "peca", "lote")}),
        (
            "Quantidade",
            {"fields": ("quantidade", "quantidade_produzida", "percentual_concluido", "status")},
        ),
        ("Registro", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
