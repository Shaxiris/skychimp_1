from django.db import models

from users.models import User


class Client(models.Model):
    """Модель для описания клиента рассылки"""

    email = models.EmailField(max_length=60, verbose_name='e-mail')
    name = models.CharField(max_length=150, verbose_name='ФИО')
    comment = models.TextField(null=True, blank=True, verbose_name='Комментарий')

    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Пользователь')

    def __str__(self):
        return f"{self.name} {self.email}"

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['name']


class Message(models.Model):
    """Модель для сообщения конкретной рассылки"""

    subject = models.CharField(default='No subject', max_length=100, verbose_name='Тема')
    body = models.TextField(null=True, blank=True, verbose_name='Тело письма')

    def __str__(self):
        return self.subject

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Mailing(models.Model):
    """
    Модель для описания рассылки, её содержимого и настроек.
    Ключевая модель приложения
    """

    FREQUENCY = (
        ('daily', 'ежедневно'),
        ('weekly', 'еженедельно'),
        ('monthly', 'ежемесячно')
    )

    STATUSES = (
        ('created', 'создана'),
        ('started', 'запущена'),
        ('finished', 'завершена')
    )

    # Расписание рассылок
    SCHEDULE = {
        FREQUENCY[0][0]: 1,
        FREQUENCY[1][0]: 7,
        FREQUENCY[2][0]: 30
    }

    start_time = models.DateTimeField(verbose_name='Время начала')
    end_time = models.DateTimeField(null=True, blank=True, verbose_name='Время окончания')
    frequency = models.CharField(max_length=7, choices=FREQUENCY, verbose_name='Периодичность')
    status = models.CharField(max_length=8, default='created', choices=STATUSES, verbose_name='Статус')
    updated_at = models.DateTimeField(auto_now=True)

    recipients = models.ManyToManyField(Client, blank=True, verbose_name='Получатели')
    message = models.ForeignKey(Message, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Сообщение')
    owner = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, verbose_name='Пользователь')

    def __str__(self):
        return f'{self.message}: {self.status} ({self.frequency})'

    class Meta:
        verbose_name = 'Рассылка'
        verbose_name_plural = 'Рассылки'


class Log(models.Model):
    """
    Модель для описания лога рассылки, создаваемого в момент отправки
    сообщения рассылки конкретному клиенту этой рассылки
    """

    STATUSES = (
        ('successful', 'успешно'),
        ('error', 'ошибка')
    )

    last_try = models.DateTimeField(auto_now_add=True, verbose_name='Дата и время последней попытки')
    status = models.CharField(max_length=10, choices=STATUSES, verbose_name='Статус попытки')
    server_response = models.CharField(null=True, blank=True, max_length=3, verbose_name='Ответ сервера')

    client = models.ForeignKey(Client, on_delete=models.CASCADE, verbose_name='Клиент')
    mailing = models.ForeignKey(Mailing, on_delete=models.CASCADE, verbose_name='Рассылка')

    def __str__(self):
        return f'{self.last_try}: {self.server_response}, {self.status}'

    class Meta:
        verbose_name = 'Лог'
        verbose_name_plural = 'Логи'

