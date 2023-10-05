from django.db import models


class BlogEntry(models.Model):
    """Класс для описания записи блога"""

    title = models.CharField(max_length=150, verbose_name='Заголовок')
    content = models.TextField(verbose_name='Запись')
    image = models.ImageField(upload_to='blog/', default='blog/image.png', verbose_name='Изображение')
    views_number = models.PositiveSmallIntegerField(default=0, verbose_name='Количество просмотров')
    publication_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')

    def __str__(self):
        return f'{self.publication_date}: {self.title}'

    class Meta:
        verbose_name = 'Запись блога'
        verbose_name_plural = 'Записи блога'
