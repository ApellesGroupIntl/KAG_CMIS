from django.apps import AppConfig


class UssdCoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'USSD_CORE'

    def ready(self):
        import USSD_CORE.signals  # noqa
