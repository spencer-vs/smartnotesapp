from django.apps import AppConfig


class NoteAppApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "NoteAppApi"

    def ready(self):
        import NoteAppApi.signals