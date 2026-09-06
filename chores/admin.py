from django.contrib import admin
from . import models


@admin.register(models.Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'emoji', 'hue', 'created_at')


@admin.register(models.Chore)
class ChoreAdmin(admin.ModelAdmin):
    list_display = ('title', 'kind', 'freq_kind', 'due_date', 'claimed_by', 'archived')


@admin.register(models.Completion)
class CompletionAdmin(admin.ModelAdmin):
    list_display = ('chore_title', 'member', 'date', 'on_time')
