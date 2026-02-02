from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import json

from .models import Attempt, Answer
from exams.models import Question, Choice


@csrf_exempt
@require_POST
@login_required
def save_answer(request):
    """AJAX endpoint to save student answers"""
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        choice_id = data.get('choice_id')
        
        question = get_object_or_404(Question, id=question_id)
        
        # Get the user's active attempt for this exam
        try:
            attempt = Attempt.objects.get(
                student=request.user, 
                exam=question.exam, 
                is_submitted=False
            )
        except Attempt.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'No active attempt found'})
        
        # Check if attempt is expired
        if attempt.is_expired():
            attempt.is_submitted = True
            attempt.end_time = timezone.now()
            attempt.calculate_score()
            return JsonResponse({'success': False, 'error': 'Exam time expired'})
        
        # Get or create answer
        answer, created = Answer.objects.get_or_create(
            attempt=attempt,
            question=question
        )
        
        # Update the selected choice
        if choice_id:
            choice = get_object_or_404(Choice, id=choice_id, question=question)
            answer.selected_choice = choice
        else:
            answer.selected_choice = None
        
        answer.save()
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
