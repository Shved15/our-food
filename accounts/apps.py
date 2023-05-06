from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        """A method that gets called when Django starts up. Import signals module to register signal handlers."""
        import accounts.signals
