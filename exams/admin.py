from django.contrib import admin
from .models import Exam, Question, Choice


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 4
    max_num = 4


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('title', 'duration_minutes', 'start_time', 'end_time', 'is_published', 'total_questions')
    list_filter = ('is_published', 'start_time', 'created_at')
    search_fields = ('title', 'description')
    date_hierarchy = 'start_time'
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('exam', 'text_preview', 'marks')
    list_filter = ('exam', 'marks')
    search_fields = ('text',)
    inlines = [ChoiceInline]
    
    def text_preview(self, obj):
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text
    text_preview.short_description = 'Question Text'


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('question', 'text_preview', 'is_correct')
    list_filter = ('is_correct', 'question__exam')
    search_fields = ('text',)
    
    def text_preview(self, obj):
        return obj.text[:30] + "..." if len(obj.text) > 30 else obj.text
    text_preview.short_description = 'Choice Text'
