from django.apps import AppConfig

class BlogConfig(AppConfig):
    #default_auto_field = "django.db.models.BigAutoField"
    default_auto_field: str = "django.db.models.BigAutoField"
    name = "apps.blog"
