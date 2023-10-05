from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView

from blog.forms import BlogEntryForm
from blog.models import BlogEntry


class ManagerOrSuperuserMixin(UserPassesTestMixin):
    """
    Миксин для проверки принадлежности юзера к группе менеджеров или суперюзеров,
    запрещает доступ к контроллерам, если проверка возвращает False
    """

    def test_func(self) -> bool:
        user = self.request.user
        return user.groups.filter(name='Managers').exists() or user.is_superuser


class BlogEntryListView(ListView):
    """
    Класс-контроллер для страницы со всеми записями блога,
    сортированным по дате публикации от более новых к более старым.
    Право просмотра есть у всех
    """

    model = BlogEntry
    template_name = 'blog/blog_entry_list.html'
    ordering = '-publication_date'


class BlogEntryCreateView(ManagerOrSuperuserMixin, CreateView):
    """
    Класс-контроллер для создания новой записи блога.
    Право создания есть только у суперюзеров и менеджеров
    """

    model = BlogEntry
    form_class = BlogEntryForm
    template_name = 'blog/blog_entry_form.html'
    success_url = reverse_lazy('blog:blog_entry_list')
    extra_context = {
        'title': 'Создать запись блога',
        'button': 'Создать',
    }


class BlogEntryUpdateView(ManagerOrSuperuserMixin, UpdateView):
    """
    Класс-контроллер для обновления существующей записи блога
    Право изменения есть только у суперюзеров и менеджеров
    """

    model = BlogEntry
    form_class = BlogEntryForm
    template_name = 'blog/blog_entry_form.html'
    success_url = reverse_lazy('blog:blog_entry_list')
    extra_context = {
        'title': 'Изменить запись блога',
        'button': 'Сохранить',
    }


class BlogEntryDeleteView(ManagerOrSuperuserMixin, DeleteView):
    """
    Класс-контроллер для удаления существующей записи блога
    Право удаления есть только у суперюзеров и менеджеров
    """

    model = BlogEntry
    template_name = 'blog/blog_entry_delete.html'
    success_url = reverse_lazy('blog:blog_entry_list')


class BlogEntryDetailView(DetailView):
    """
    Класс-контроллер для просмотра полной версии существующей записи блога
    Право просмотра есть у всех
    """

    model = BlogEntry
    template_name = 'blog/blog_entry_detail.html'

    def get_context_data(self, **kwargs) -> dict:
        """Добавляет в контекст ссылку для возврата на предыдущую страницу"""

        context = super().get_context_data(**kwargs)
        context['referer'] = self.request.META.get('HTTP_REFERER')
        return context

    def get(self, request, *args, **kwargs) -> HttpResponse:
        """
        Позволяет увеличить на 1 число просмотров записи блога,
        при открытии её полной версии
        """

        response = super().get(request, *args, **kwargs)
        self.object.views_number += 1
        self.object.save()

        return response
