from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Usuario, LogAcao


@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    """Admin customizado para o modelo Usuario."""

    list_display = ("email", "first_name", "last_name", "is_active", "is_staff", "created_at")
    list_filter = ("is_active", "is_staff", "is_superuser", "created_at")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("-created_at",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Informações Pessoais", {"fields": ("first_name", "last_name")}),
        (
            "Permissões",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("Datas", {"fields": ("created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    readonly_fields = ("created_at", "updated_at")


@admin.register(LogAcao)
class LogAcaoAdmin(admin.ModelAdmin):
    """Admin para o modelo LogAcao."""

    list_display = ("acao", "usuario", "alvo_tipo", "alvo_id", "created_at")
    list_filter = ("acao", "alvo_tipo", "created_at")
    search_fields = ("acao", "usuario__email", "alvo_tipo")
    readonly_fields = ("usuario", "acao", "alvo_tipo", "alvo_id", "detalhes", "created_at")
    ordering = ("-created_at",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
