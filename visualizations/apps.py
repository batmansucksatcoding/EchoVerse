from django.apps import AppConfig


class VisualizationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'visualizations'

    def ready(self):
        import visualizations.signals
