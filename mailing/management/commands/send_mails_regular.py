from django.core.management import BaseCommand
from mailing import services


class Command(BaseCommand):
    """
    Кастомная консольная команда, позволяющая отправить письма клиентам,
    указанным в качестве получателей в тех рассылках, статус которых указан
    как 'started'.

    Если время и дата окончания рассылки меньше, чем время на момент исполнения команды,
    то рассылка переводится в статус 'finished'
    """

    def handle(self, *args, **options) -> None:
        services.send_mails_regular()
