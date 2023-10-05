from django.core.mail import send_mail
from config import settings


def send_verification_url(email: str, url: str) -> None:
    """Функция для отправки ссылки верификации на почту юзера"""

    send_mail(
        subject='Вам выслана ссылка для верификации почтового адреса!',
        message=f'Пожалуйста, пройдите по этой ссылке для окончания регистрации на сайте:\n'
                f'{url}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )