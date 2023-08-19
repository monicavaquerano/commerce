from django.apps import AppConfig


class AuctionsConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "auctions"

    def ready(self) -> None:
        from jobs import updater

        updater.start()
