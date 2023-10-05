from django.contrib.auth.models import Group
from django.core.management import BaseCommand


class Command(BaseCommand):
    """Кастомная консольная команда для создания группы менеджеров ('Managers')"""

    def handle(self, *args, **options) -> None:
        group, created = Group.objects.get_or_create(name='Managers')
        if created:
            print('Группа "Managers" была успешно создана')
        else:
            print('Группа "Managers" уже существует')
