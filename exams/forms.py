from django import forms
from .models import Exam, Question, Choice, Category


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ['category', 'title', 'description', 'duration_minutes', 'start_time', 'end_time', 'is_published']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'duration_minutes': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'start_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Convert datetime to the format expected by datetime-local input
        if self.instance.pk:
            if self.instance.start_time:
                self.initial['start_time'] = self.instance.start_time.strftime('%Y-%m-%dT%H:%M')
            if self.instance.end_time:
                self.initial['end_time'] = self.instance.end_time.strftime('%Y-%m-%dT%H:%M')


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['text', 'image', 'marks', 'time_limit_seconds', 'explanation']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 1}),
            'time_limit_seconds': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'explanation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ChoiceForm(forms.ModelForm):
    class Meta:
        model = Choice
        fields = ['text', 'is_correct']
        widgets = {
            'text': forms.TextInput(attrs={'class': 'form-control'}),
            'is_correct': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuestionBulkUploadForm(forms.Form):
    """Simple form for uploading a CSV with questions and choices."""

    file = forms.FileField(
        label="Question file (CSV)",
        help_text="Upload a .csv file with columns: question, option1, option2, option3, option4, correct, marks, explanation, time_limit_seconds",
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    clear_existing = forms.BooleanField(
        required=False,
        initial=False,
        label="Remove existing questions before import",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )