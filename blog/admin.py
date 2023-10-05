from django.contrib import admin
from blog.models import BlogEntry


@admin.register(BlogEntry)
class BlogEntryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'content', 'image', 'views_number', 'publication_date')
    search_fields = ('title', 'publication_date')
    list_filter = ('publication_date',)

