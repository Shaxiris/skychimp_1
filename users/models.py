from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Модель для описания пользователя"""

    email = models.EmailField(unique=True, verbose_name='E-mail')
    phone = models.CharField(null=True, blank=True, max_length=60, verbose_name='Телефон')
    username = models.CharField(null=True, blank=True, max_length=150, verbose_name='Имя')

    is_active = models.BooleanField(
        _("active"),
        default=False,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )

    verification_code = models.CharField(max_length=15,
                                         unique=True,
                                         null=True,
                                         blank=True,
                                         verbose_name='Код верификации')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
