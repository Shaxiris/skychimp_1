from django.core.management import BaseCommand
from django.utils import timezone
from mailing.models import Mailing
from mailing import services


class Command(BaseCommand):
    """
    Кастомная консольная команда, позволяющая изменить статус всех рассылок,
    у которых уже наступило время старта на момент исполнения команды,
    с 'created' на 'started'
    """

    def handle(self, *args, **options) -> None:
        services.change_status_to_started()
