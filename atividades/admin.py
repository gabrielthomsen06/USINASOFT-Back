from django.contrib import admin
from .models import Atividade, Comentario, Anexo


class ComentarioInline(admin.TabularInline):
    """Inline para exibir comentários no admin de Atividade."""

    model = Comentario
    extra = 1
    readonly_fields = ("created_at",)


@admin.register(Atividade)
class AtividadeAdmin(admin.ModelAdmin):
    """Admin para o modelo Atividade."""

    list_display = (
        "titulo",
        "status",
        "responsavel",
        "prioridade",
        "ordem",
        "peca",
        "data_inicio",
        "data_fim",
    )
    list_filter = ("status", "prioridade", "responsavel", "created_at")
    search_fields = ("titulo", "descricao", "responsavel__email", "ordem__numero", "peca__codigo")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    inlines = [ComentarioInline]

    fieldsets = (
        ("Informações Básicas", {"fields": ("titulo", "descricao", "responsavel")}),
        ("Relacionamentos", {"fields": ("ordem", "ordem_item", "peca")}),
        ("Status e Prioridade", {"fields": ("status", "prioridade", "posicao")}),
        ("Datas", {"fields": ("data_inicio", "data_fim")}),
        ("Metadados", {"fields": ("metadata",), "classes": ("collapse",)}),
        ("Registro", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    """Admin para o modelo Comentario."""

    list_display = ("atividade", "autor", "texto_resumido", "created_at")
    list_filter = ("created_at", "autor")
    search_fields = ("texto", "autor__email", "atividade__titulo")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    def texto_resumido(self, obj):
        """Retorna um resumo do texto."""
        return obj.texto[:50] + "..." if len(obj.texto) > 50 else obj.texto

    texto_resumido.short_description = "Texto"


@admin.register(Anexo)
class AnexoAdmin(admin.ModelAdmin):
    """Admin para o modelo Anexo."""

    list_display = ("nome_original", "content_type", "criado_por", "tamanho", "created_at")
    list_filter = ("content_type", "created_at", "mime_type")
    search_fields = ("nome_original", "arquivo_path", "criado_por__email")
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    fieldsets = (
        (
            "Informações do Arquivo",
            {"fields": ("arquivo_path", "nome_original", "mime_type", "tamanho")},
        ),
        ("Relacionamento", {"fields": ("content_type", "object_id")}),
        (
            "Metadados",
            {
                "fields": ("metadata", "criado_por"),
            },
        ),
        ("Registro", {"fields": ("created_at",), "classes": ("collapse",)}),
    )
