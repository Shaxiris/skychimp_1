from django.contrib import admin
from mailing.models import Client, Message, Log, Mailing

# Register your models here.


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'comment')
    search_fields = ('name', 'email')
    list_filter = ('name',)


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject', 'body')
    search_fields = ('subject',)
    list_filter = ('subject',)


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('last_try', 'status', 'server_response', 'client', 'mailing')
    search_fields = ('last_try', 'status', 'server_response')
    list_filter = ('last_try', 'status', 'server_response')


@admin.register(Mailing)
class MailingAdmin(admin.ModelAdmin):
    list_display = ('start_time', 'end_time', 'frequency', 'status', 'message')
    search_fields = ('start_time', 'end_time', 'frequency', 'status', 'message')
    list_filter = ('start_time', 'end_time', 'frequency', 'status', 'message')
