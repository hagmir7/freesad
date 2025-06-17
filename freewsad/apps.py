from django.apps import AppConfig


class FreewsadConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "freewsad"

    def ready(self):
        import freewsad.signals  # Make sure 'signals.py' exists in your app
