from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json

from .models import Exam, Question, Choice
from attempts.models import Attempt, Answer


@login_required
def student_dashboard(request):
    """Student dashboard showing available exams"""
    exams = Exam.objects.filter(is_published=True).order_by('-created_at')
    exam_statuses = []
    
    for exam in exams:
        try:
            attempt = Attempt.objects.get(student=request.user, exam=exam)
            if attempt.is_submitted:
                status = 'Completed'
            elif attempt.is_expired():
                # Auto-submit expired attempt
                attempt.is_submitted = True
                attempt.end_time = timezone.now()
                attempt.calculate_score()
                status = 'Completed'
            else:
                status = 'In Progress'
        except Attempt.DoesNotExist:
            if exam.is_active():
                status = 'Available'
            else:
                status = 'Not Available'
        
        exam_statuses.append({
            'exam': exam,
            'status': status,
            'attempt': attempt if 'attempt' in locals() else None
        })
        
        # Clear attempt variable for next iteration
        if 'attempt' in locals():
            del attempt
    
    return render(request, 'exams/student_dashboard.html', {
        'exam_statuses': exam_statuses
    })


@login_required
def exam_detail(request, exam_id):
    """Show exam details before starting"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    
    # Check if user already has an attempt
    try:
        attempt = Attempt.objects.get(student=request.user, exam=exam)
        if attempt.is_submitted:
            return redirect('results:result_detail', attempt_id=attempt.id)
        elif attempt.is_expired():
            # Auto-submit expired attempt
            attempt.is_submitted = True
            attempt.end_time = timezone.now()
            attempt.calculate_score()
            return redirect('results:result_detail', attempt_id=attempt.id)
        else:
            # Continue existing attempt
            return redirect('student:take_exam', exam_id=exam.id)
    except Attempt.DoesNotExist:
        pass
    
    if not exam.is_active():
        messages.error(request, 'This exam is not currently available.')
        return redirect('student:dashboard')
    
    return render(request, 'exams/exam_detail.html', {'exam': exam})


@login_required
def start_exam(request, exam_id):
    """Start a new exam attempt"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    
    # Check if exam is active
    if not exam.is_active():
        messages.error(request, 'This exam is not currently available.')
        return redirect('student:dashboard')
    
    # Check if user already has an attempt
    try:
        attempt = Attempt.objects.get(student=request.user, exam=exam)
        if attempt.is_submitted:
            messages.info(request, 'You have already completed this exam.')
            return redirect('results:result_detail', attempt_id=attempt.id)
        else:
            return redirect('student:take_exam', exam_id=exam.id)
    except Attempt.DoesNotExist:
        pass
    
    if request.method == 'POST':
        # Create new attempt
        attempt = Attempt.objects.create(
            student=request.user,
            exam=exam,
            start_time=timezone.now()
        )
        
        # Create answer objects for all questions
        for question in exam.questions.all():
            Answer.objects.create(
                attempt=attempt,
                question=question
            )
        
        messages.success(request, 'Exam started! Good luck!')
        return redirect('student:take_exam', exam_id=exam.id)
    
    return render(request, 'exams/start_exam.html', {'exam': exam})


@login_required
def take_exam(request, exam_id):
    """Take the exam interface"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    
    # Get the attempt
    try:
        attempt = Attempt.objects.get(student=request.user, exam=exam)
    except Attempt.DoesNotExist:
        messages.error(request, 'No active attempt found. Please start the exam first.')
        return redirect('student:exam_detail', exam_id=exam.id)
    
    # Check if already submitted
    if attempt.is_submitted:
        return redirect('results:result_detail', attempt_id=attempt.id)
    
    # Check if expired
    if attempt.is_expired():
        attempt.is_submitted = True
        attempt.end_time = timezone.now()
        attempt.calculate_score()
        messages.info(request, 'Time is up! Your exam has been auto-submitted.')
        return redirect('results:result_detail', attempt_id=attempt.id)
    
    # Get current question (from GET parameter, default to first)
    current_question_index = int(request.GET.get('q', 1)) - 1
    questions = list(exam.questions.all())
    
    if current_question_index >= len(questions) or current_question_index < 0:
        current_question_index = 0
    
    current_question = questions[current_question_index]
    
    # Get existing answer for this question
    try:
        answer = Answer.objects.get(attempt=attempt, question=current_question)
    except Answer.DoesNotExist:
        answer = Answer.objects.create(attempt=attempt, question=current_question)
    
    # Get all answers for progress tracking
    answers = {a.question_id: a.selected_choice_id for a in attempt.answers.all()}
    
    context = {
        'exam': exam,
        'attempt': attempt,
        'current_question': current_question,
        'current_index': current_question_index,
        'total_questions': len(questions),
        'answers': answers,
        'time_remaining': attempt.time_remaining(),
    }
    
    return render(request, 'exams/take_exam.html', context)


@csrf_exempt
@require_POST
@login_required
def submit_exam(request, exam_id):
    """Submit the exam or save answer via AJAX"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)
    
    try:
        attempt = Attempt.objects.get(student=request.user, exam=exam)
    except Attempt.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No active attempt found'})
    
    if attempt.is_submitted:
        return JsonResponse({'success': False, 'error': 'Exam already submitted'})
    
    # Handle AJAX answer saving
    if request.headers.get('Content-Type') == 'application/json':
        try:
            data = json.loads(request.body)
            question_id = data.get('question_id')
            choice_id = data.get('choice_id')
            
            question = get_object_or_404(Question, id=question_id, exam=exam)
            choice = get_object_or_404(Choice, id=choice_id, question=question) if choice_id else None
            
            answer, created = Answer.objects.get_or_create(
                attempt=attempt,
                question=question,
                defaults={'selected_choice': choice}
            )
            
            if not created:
                answer.selected_choice = choice
                answer.save()
            
            return JsonResponse({'success': True})
            
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    # Handle final exam submission
    if request.method == 'POST' and 'submit_exam' in request.POST:
        attempt.is_submitted = True
        attempt.end_time = timezone.now()
        attempt.calculate_score()
        
        messages.success(request, 'Exam submitted successfully!')
        return redirect('results:result_detail', attempt_id=attempt.id)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})
