import os

from django.core.management import BaseCommand
from users.models import User


class Command(BaseCommand):
    """
    Кастомная консольная команда для создания суперпользователя,
    e-mail и пароль для суперюзера загружаются из файла .env
    """

    def handle(self, *args, **options) -> None:
        user = User.objects.create(
            email=os.getenv('SUPERUSER_EMAIL'),
            is_staff=True,
            is_superuser=True,
            is_active=True
        )
        user.set_password(os.getenv('SUPERUSER_PASSWORD'))
        user.save()

        print('Создан суперпользователь')
