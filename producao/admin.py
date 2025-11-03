from django.contrib import admin
from .models import OrdemProducao


@admin.register(OrdemProducao)
class OrdemProducaoAdmin(admin.ModelAdmin):
    """Admin para o modelo OrdemProducao."""

    list_display = (
        "codigo",
        "cliente",
        "criado_por",
        "status",
        "total_pecas",
        "percentual_conclusao",
        "created_at",
    )
    list_filter = ("status", "created_at", "cliente")
    search_fields = ("codigo", "cliente__nome", "criado_por__email", "observacoes")
    readonly_fields = (
        "created_at",
        "updated_at",
        "total_pecas",
        "pecas_concluidas",
        "percentual_conclusao",
    )
    ordering = ("-created_at",)

    fieldsets = (
        ("Informações Básicas", {"fields": ("codigo", "cliente", "criado_por", "status")}),
        ("Observações", {"fields": ("observacoes",)}),
        (
            "Estatísticas",
            {
                "fields": ("total_pecas", "pecas_concluidas", "percentual_conclusao"),
                "classes": ("collapse",),
            },
        ),
        ("Registro", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
