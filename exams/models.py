from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Exam(models.Model):
    """Model for storing exam information"""
    title = models.CharField(max_length=200)
    description = models.TextField()
    duration_minutes = models.PositiveIntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title
    
    def is_active(self):
        """Check if exam is currently active"""
        now = timezone.now()
        return self.is_published and self.start_time <= now <= self.end_time
    
    def total_questions(self):
        """Get total number of questions in this exam"""
        return self.questions.count()
    
    def total_marks(self):
        """Get total marks for this exam"""
        return sum(q.marks for q in self.questions.all())


class Question(models.Model):
    """Model for storing MCQ questions"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    marks = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.exam.title} - Q{self.id}"
    
    def get_correct_choice(self):
        """Get the correct choice for this question"""
        return self.choices.filter(is_correct=True).first()


class Choice(models.Model):
    """Model for storing MCQ choices"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.question.exam.title} - Q{self.question.id} - {self.text[:50]}"
