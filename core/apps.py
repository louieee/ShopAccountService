from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        # Import the module here to avoid side effects on Django startup
        import signal # noqa
        from core.services.rabbit_mq_service.main import rabbit_mq_service
        rabbit_mq_service.consume_in_background()

