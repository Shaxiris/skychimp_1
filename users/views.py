import secrets

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.views import LoginView as BaseLoginView
from django.forms import Form
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, ListView
from django.contrib import messages
from users import services
from users.forms import LoginForm, UserRegisterForm, UserForm
from users.models import User


class LoginView(BaseLoginView):
    """Класс-контроллер для отображения страницы входа пользователя"""

    template_name = 'users/login.html'
    form_class = LoginForm


class UserUpdateView(UpdateView):
    """Класс-контроллер для отображения страницы изменения профиля пользователя"""

    model = User
    template_name = 'users/user_update.html'
    form_class = UserForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None) -> User:
        return self.request.user


class RegisterView(CreateView):
    """
    Класс-контроллер для отображения страницы регистрации нового пользователя.
    При регистрации на почту пользователя отправляется ссылка для прохождения верификации,
    о чем предупреждает всплывающее сообщение
    """

    model = User
    template_name = 'users/registration.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form: Form) -> HttpResponse:
        if form.is_valid():
            self.object = form.save(commit=False)
            verification_code = secrets.token_urlsafe(nbytes=11)
            self.object.verification_code = verification_code

            url = reverse('users:verification', args=[verification_code])
            absolute_url = self.request.build_absolute_uri(url)
            services.send_verification_url(email=self.object.email,
                                           url=absolute_url)
            messages.success(self.request, 'Ссылка для верификации отправлена на вашу электронную почту!')
            self.object.save()

        return super().form_valid(form)


def verification(request, verification_code: str) -> HttpResponse:
    """
    Контроллер для активации пользователя при переходе по верификационной ссылке.
    Ссылка является одноразовой, так как после активации пользователя верификационный код
    удаляется из модели пользователя
    """

    user = User.objects.get(verification_code=verification_code)
    user.is_active = True
    user.verification_code = None
    user.save()
    return redirect(reverse('users:login'))


class UserListView(UserPassesTestMixin, ListView):
    """
    Класс-контроллер для отображения страницы со списком всех зарегистрированных пользователей.
    Страница доступна только менеджерам и суперюзерам
    """

    model = User
    template_name = 'users/users_list.html'
    ordering = 'email'

    def test_func(self) -> bool:
        user = self.request.user
        is_manager = user.groups.filter(name='Managers').exists()
        return user.is_superuser or is_manager


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Managers').exists())
def deactivate_user(request, pk: int) -> HttpResponse:
    """
    Контроллер для изменения статуса пользователя с активного на неактивный и наоборот.
    Доступ к контроллеру есть только у менеджеров и суперюзеров
    """

    user = get_object_or_404(User, pk=pk)
    user.is_active = not user.is_active
    user.save()

    return redirect('users:users_list')

