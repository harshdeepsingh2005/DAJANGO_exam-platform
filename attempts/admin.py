from django.contrib import admin
from .models import Attempt, Answer


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'selected_choice', 'created_at', 'updated_at')


@admin.register(Attempt)
class AttemptAdmin(admin.ModelAdmin):
    list_display = ('student', 'exam', 'start_time', 'is_submitted', 'score')
    list_filter = ('is_submitted', 'exam', 'start_time')
    search_fields = ('student__username', 'exam__title')
    readonly_fields = ('start_time', 'end_time', 'score')
    inlines = [AnswerInline]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('attempt', 'question', 'selected_choice', 'updated_at')
    list_filter = ('attempt__exam', 'created_at')
    search_fields = ('attempt__student__username', 'question__text')
    readonly_fields = ('created_at', 'updated_at')
