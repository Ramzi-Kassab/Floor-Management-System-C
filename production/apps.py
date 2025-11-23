from django.apps import AppConfig


class ProductionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "production"

    def ready(self):
        """
        Import signals when Django starts
        """
        import production.signals  # noqa
