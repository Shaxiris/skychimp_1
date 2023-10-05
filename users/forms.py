from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.core.exceptions import ValidationError

from users.models import User


class StyleFormMixin:
    """Миксин для установки определенных стилей доя форм"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['style'] = 'text-align: center;'


class LoginForm(StyleFormMixin, AuthenticationForm):
    """Форма для аутентификации пользователя"""

    pass


class UserRegisterForm(StyleFormMixin, UserCreationForm):
    """Форма для регистрации пользователя"""

    class Meta:
        model = User
        fields = ('email', 'username', 'phone', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password1'].help_text = None

    def clean_phone(self):
        cleaned_data = self.cleaned_data.get('phone')
        if cleaned_data:
            for sign in list(cleaned_data):
                if sign.isalpha():
                    raise ValidationError('Номер телефона не должен содержать буквы!')

            return cleaned_data.strip()


class UserForm(StyleFormMixin, UserChangeForm):
    """Форма для изменения профиля пользователя"""

    class Meta:
        model = User
        fields = ('phone', 'username')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = forms.HiddenInput()
        self.fields['password'].label = False
