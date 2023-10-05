from django import forms
from django.forms import DateTimeInput

from mailing.models import Client, Message, Mailing


class StyleFormMixin:
    """Миксин для подключения единого стиля к формам"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ClientForm(StyleFormMixin, forms.ModelForm):
    """
    Форма для модели Клиента (Client).

    Устанавливает поле comment как необязательное с соответствующей пометкой
    """

    comment = forms.CharField(
        required=False,
        label='* Комментарий',
        widget=forms.Textarea()
    )

    class Meta:
        model = Client
        fields = ('email', 'comment')


class MessageForm(StyleFormMixin, forms.ModelForm):
    """
    Форма для модели Сообщения (Message).

    Устанавливает по умолчанию высоту области ввода тела письма равной 3 строкам
    """

    class Meta:
        model = Message
        fields = '__all__'
        labels = {
            'subject': 'Тема',
            'body': 'Тело письма',
        }
        widgets = {
            'body': forms.Textarea(attrs={'rows': 3}),
        }


class MailingForm(StyleFormMixin, forms.ModelForm):
    """
    Форма для модели Рассылки (Mailing).
    Ключевая модель приложения.

    Устанавливает специальные виджеты на поля типа DateTimeField (в виде календаря)
    и для поля recipients загружает коллекцию клиентов для множественного выбора.
    Коллекция клиентов зависит от группы, к которой принадлежит пользователь и его статуса
    """

    start_time = forms.DateTimeField(
        label='Время начала',
        widget=DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%dT%H:%M')
    )
    end_time = forms.DateTimeField(
        label='Время окончания',
        widget=DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}, format='%Y-%m-%dT%H:%M')
    )
    recipients = forms.ModelMultipleChoiceField(
        label='Получатели',
        queryset=Client.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'})
    )

    def __init__(self, *args, **kwargs):
        """
        На основе переданного при создании объекта модели User
        загружает из базы данных и передает в форму коллекцию клиентов,
        которые ссылаются на этого пользователя.
        В случае если юзер не авторизован, передает пустую коллекцию
        """

        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_authenticated:
            self.fields['recipients'].queryset = Client.objects.filter(owner=user)
        else:
            self.fields['recipients'].queryset = Client.objects.none()

    class Meta:
        model = Mailing
        exclude = ('status', 'message', 'updated_at', 'owner')
