from django.apps import AppConfig


class PecasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "pecas"
    verbose_name = "Peças"

    def ready(self):
        # Importa os sinais quando o app é carregado
        import pecas.signals
