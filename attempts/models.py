from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from exams.models import Exam, Question, Choice


class Attempt(models.Model):
    """Model for storing student exam attempts"""
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='attempts')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    is_submitted = models.BooleanField(default=False)
    score = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'exam')  # One attempt per exam per student
    
    def __str__(self):
        return f"{self.student.username} - {self.exam.title}"
    
    def is_expired(self):
        """Check if attempt has expired based on exam duration"""
        if not self.start_time:
            return False
        expected_end_time = self.start_time + timezone.timedelta(minutes=self.exam.duration_minutes)
        return timezone.now() > expected_end_time
    
    def time_remaining(self):
        """Get remaining time in seconds"""
        if self.is_submitted:
            return 0
        expected_end_time = self.start_time + timezone.timedelta(minutes=self.exam.duration_minutes)
        remaining = expected_end_time - timezone.now()
        return max(0, int(remaining.total_seconds()))
    
    def calculate_score(self):
        """Calculate and update the score for this attempt"""
        correct_answers = 0
        total_marks = 0
        
        for answer in self.answers.all():
            if answer.selected_choice and answer.selected_choice.is_correct:
                correct_answers += 1
                total_marks += answer.question.marks
        
        self.score = total_marks
        self.save()
        return total_marks


class Answer(models.Model):
    """Model for storing student answers"""
    attempt = models.ForeignKey(Attempt, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_choice = models.ForeignKey(Choice, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('attempt', 'question')  # One answer per question per attempt
    
    def __str__(self):
        return f"{self.attempt.student.username} - {self.question.exam.title} - Q{self.question.id}"
