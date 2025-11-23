# HR App - Floor Management System
from django.apps import AppConfig


class HRConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'
    verbose_name = 'Human Resources'

    def ready(self):
        """Import signals when app is ready."""
        # Import signals here if needed in the future
        pass
