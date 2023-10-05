from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import QuerySet
from django.forms import inlineformset_factory, Form
from django.http import Http404, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView

from blog.models import BlogEntry
from mailing import services
from mailing.forms import ClientForm, MailingForm, MessageForm
from mailing.models import Client, Message, Log, Mailing


class MailingAndMessageSaveMixin:
    """
    Миксин, который обуславливает основное поведение при создании
    и изменении объекта рассылки (Mailing) вместе с объектом сообщения (Message),
    связанным с рассылкой
    """

    def get_form_kwargs(self) -> dict:
        """
        Получение и передача объекта текущего юзера в словарь
        с аргументами для инициализации формы
        """

        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs) -> dict:
        """
        Получение данных контекста для шаблона.

        Обуславливает отображение формы сообщения вместе с основной формой страницы
        """

        context_data = super().get_context_data(**kwargs)

        if self.request.POST:
            context_data['message_form'] = MessageForm(self.request.POST)
        else:
            if self.object and self.object.message:
                context_data['message_form'] = MessageForm(instance=self.object.message)
            else:
                context_data['message_form'] = MessageForm()
        return context_data

    def form_valid(self, form: Form) -> HttpResponse:
        """
        Обработка действий при валидности формы.

        Обуславливает сохранение объекта и связанного с ним объекта сообщения (Message),
        при условии, что форма валидна, а юзер авторизован.
        Присваивает объекту в качестве владельца (поле owner) текущего юзера
        """

        context_data = self.get_context_data()
        message_form = context_data['message_form']
        self.object = form.save(commit=False)

        if message_form.is_valid() and self.request.user.is_authenticated:
            message = message_form.save()
            self.object.message = message
            self.object.owner = self.request.user
            self.object.save()
            return super().form_valid(form)
        else:
            return self.form_invalid(form)


class OnlyForOwnerOrSuperuserMixin:
    """
    Миксин, ограничивающий демонстрацию страницы объекта для пользователя,
    который не является ни владельцем объекта, ни суперюзером
    """

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        if self.object.owner != self.request.user and not self.request.user.is_superuser:
            raise Http404
        return self.object


class HomeView(MailingAndMessageSaveMixin, CreateView):
    """
    Класс-контроллер для отображения домашней страницы.

    Особенность этой домашней страницы в наличии формы создания рассылки
    """

    model = Mailing
    template_name = 'mailing/home.html'
    form_class = MailingForm
    success_url = reverse_lazy('mailing:home')
    extra_context = {'button': 'Создать', }

    def get_context_data(self, **kwargs) -> dict:
        """
        Отвечает за передачу в контекст информации, которая используется
        для построения некоторой статистики пользователя:
        общее количество рассылок, количество активных рассылок, общее количество клиентов.

        Также добавляет 3 случайные статьи блога (BlogEntry) в контекст
        """

        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            card_info = services.cache_statistic_card(user)
            context.update(card_info)
        context['object_list'] = BlogEntry.objects.order_by('?')[:3]
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    """
    Класс-контроллер для создания клиента (Client)
    """

    model = Client
    template_name = 'mailing/recipient_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('mailing:recipients_list')
    extra_context = {
        'title': 'Создать контакт',
        'button': 'Создать',
    }

    def form_valid(self, form: Form) -> HttpResponse:
        """
        Обработка действий при валидности формы.

        Обрабатывает поля ФИО, объединяя их в одно поле name
        """

        last_name = self.request.POST.get('last_name', '').strip()
        first_name = self.request.POST.get('first_name', '').strip()
        father_name = self.request.POST.get('father_name', '').strip()

        full_name = f"{last_name} {first_name} {father_name}".strip().title()

        form.instance.name = full_name

        self.object = form.save()
        self.object.owner = self.request.user

        return super().form_valid(form)


class ClientListView(LoginRequiredMixin, ListView):
    """
    Класс-контроллер для отображения списка клиентов.

    Просмотр доступен только авторизованным пользователям.
    Список клиентов зависит от статуса текущего пользователя:
    обычный юзер может видеть только клиентов, которых он создавал,
    менеджер и суперюзер могут видеть весь перечень клиентов,
    существующий в базе данных
    """

    model = Client
    template_name = 'mailing/recipients_list.html'

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        is_manager = user.groups.filter(name='Managers').exists()
        if user.is_superuser or is_manager:
            queryset = super().get_queryset().all()
        else:
            queryset = super().get_queryset().filter(owner=user)
        return queryset.order_by('name')


class ClientUpdateView(LoginRequiredMixin, OnlyForOwnerOrSuperuserMixin, UpdateView):
    """
    Класс-контроллер для редактирования клиента (Client).

    Доступ к странице есть либо у создателя этого клиента,
    либо у суперюзера
    """

    model = Client
    template_name = 'mailing/recipient_form.html'
    success_url = reverse_lazy('mailing:recipients_list')
    form_class = ClientForm

    def get_context_data(self, **kwargs) -> dict:
        """
        Добавление в контекст конкретного объекта модели Client,
        а также надписи в заголовке и на кнопке
        """

        context_data = super().get_context_data(**kwargs)
        extra_context = {
            'object': Client.objects.get(pk=self.kwargs.get('pk')),
            'title': 'Изменить контакт',
            'button': 'Сохранить',
        }
        return context_data | extra_context

    def form_valid(self, form):
        """
        Обработка действий при валидности формы.

        Обрабатывает поля ФИО, объединяя их в одно поле name
        """

        last_name = self.request.POST.get('last_name', '').strip()
        first_name = self.request.POST.get('first_name', '').strip()
        father_name = self.request.POST.get('father_name', '').strip()

        full_name = f"{last_name} {first_name} {father_name}".strip().title()

        form.instance.name = full_name

        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, OnlyForOwnerOrSuperuserMixin, DeleteView):
    """
    Класс-контроллер для удаления конкретного клиента
    """

    model = Client
    template_name = 'mailing/recipient_delete.html'
    success_url = reverse_lazy('mailing:recipients_list')

    def get_context_data(self, **kwargs) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data['object'] = Client.objects.get(pk=self.kwargs.get('pk'))
        return context_data


class MailingListView(LoginRequiredMixin, ListView):
    """
    Класс-контроллер для отображения списка рассылок.

    Обычный пользователь может видеть только те рассылки, которые создал сам,
    менеджеры и суперюзеры могут видеть весь существующий список рассылок
    """

    model = Mailing
    template_name = 'mailing/mailing_list.html'

    def get_queryset(self) -> QuerySet:
        user = self.request.user
        is_manager = user.groups.filter(name='Managers').exists()
        if user.is_superuser or is_manager:
            queryset = super().get_queryset().all()
        else:
            queryset = super().get_queryset().filter(owner=user)
        return queryset.order_by('-updated_at')


class MailingCreateView(LoginRequiredMixin, MailingAndMessageSaveMixin, CreateView):
    """
    Класс-контроллер для создания объекта рассылки.

    Доступ к контроллеру есть только у авторизованных пользователей
    """

    model = Mailing
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm
    extra_context = {'button': 'Создать', 'title': 'Создать рассылку'}
    success_url = reverse_lazy('mailing:mailing_list')


class MailingUpdateView(LoginRequiredMixin, OnlyForOwnerOrSuperuserMixin, MailingAndMessageSaveMixin, UpdateView):
    """
    Класс-контроллер для изменения объекта рассылки.

    Доступ есть только у владельца рассылки (тот, кто создал рассылку), а также
    у суперюзера
    """

    model = Mailing
    template_name = 'mailing/mailing_form.html'
    form_class = MailingForm
    extra_context = {'button': 'Сохранить', 'title': 'Изменить рассылку'}
    success_url = reverse_lazy('mailing:mailing_list')


class MailingDeleteView(LoginRequiredMixin, OnlyForOwnerOrSuperuserMixin, DeleteView):
    """
    Класс-контроллер для удаления объекта рассылки.

    Доступ есть только у владельца рассылки (тот, кто создал рассылку), а также
    у суперюзера
    """

    model = Mailing
    template_name = 'mailing/mailing_delete.html'
    success_url = reverse_lazy('mailing:mailing_list')

    def get_context_data(self, **kwargs) -> dict:
        context_data = super().get_context_data(**kwargs)
        context_data['object'] = Mailing.objects.get(pk=self.kwargs.get('pk'))
        return context_data


class MailingDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    """
    Класс-контроллер для просмотра деталей объекта рассылки.

    Доступ есть только у владельца рассылки (тот, кто создал рассылку), а также
    у менеджеров и суперюзера
    """
    model = Mailing
    template_name = 'mailing/mailing_card.html'

    def test_func(self):
        user = self.request.user
        is_manager = user.groups.filter(name='Managers').exists()
        is_owner = user == self.get_object().owner
        return user.is_superuser or is_manager or is_owner


@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Managers').exists())
def deactivate_mailing(request, pk):
    """
    Контроллер для деактивации рассылки.

    Доступен только для суперюзеров и менеджеров
    """

    mailing = get_object_or_404(Mailing, pk=pk)
    mailing.status = Mailing.STATUSES[2][0]
    mailing.save()

    return redirect('mailing:mailing_list')

