from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_POST
import json

from .models import Exam, Question, Choice, Category
from .email_utils import send_exam_completed_email
from attempts.models import Attempt, Answer
from django.db.models import Sum, Count, F


def landing(request):
    """Public landing page with role-based CTAs.

    - Not authenticated: hero + Login / Register / Get Started→Register
    - Authenticated student: hero + Get Started→Student dashboard
    - Authenticated admin/staff: hero + Get Started→Admin panel
    """
    return render(request, 'landing.html')


@login_required
def student_dashboard(request):
    """Student dashboard showing available exams"""
    exams = Exam.objects.filter(is_published=True).order_by('-created_at')
    category_id = request.GET.get('category')
    if category_id:
        exams = exams.filter(category_id=category_id)
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
                send_exam_completed_email(attempt)
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
    
    recent_attempts = Attempt.objects.filter(student=request.user).select_related('exam').order_by('-end_time', '-start_time')[:5]
    categories = Category.objects.all()

    return render(request, 'exams/student_dashboard.html', {
        'exam_statuses': exam_statuses,
        'recent_attempts': recent_attempts,
        'categories': categories,
        'selected_category_id': category_id,
    })


@login_required
def student_profile(request):
    """Student profile with basic info and exam history"""
    attempts = Attempt.objects.filter(student=request.user).select_related('exam').order_by('-end_time', '-start_time')

    return render(request, 'exams/profile.html', {
        'attempts': attempts,
    })


@login_required
def global_leaderboard(request):
    """Global leaderboard across all submitted attempts.

    Ranks students by total score across all exams, then by average percentage.
    """

    submitted = Attempt.objects.filter(is_submitted=True).select_related('student', 'exam')

    leaderboard = (
        submitted.values('student_id', 'student__username', 'student__first_name', 'student__last_name')
        .annotate(
            exams_taken=Count('id'),
            total_score=Sum('score'),
        )
        .order_by('-total_score', 'student__username')[:50]
    )

    # Attach a simple display name
    entries = []
    for rank, row in enumerate(leaderboard, start=1):
        full_name = (row.get('student__first_name') or '').strip()
        if row.get('student__last_name'):
            full_name = (full_name + ' ' + row.get('student__last_name')).strip()
        display_name = full_name or row.get('student__username')
        entries.append({
            'rank': rank,
            'display_name': display_name,
            'exams_taken': row['exams_taken'],
            'total_score': row['total_score'],
        })

    return render(request, 'exams/global_leaderboard.html', {
        'entries': entries,
    })


@login_required
def exam_leaderboard(request, exam_id):
    """Leaderboard for a specific exam (submitted attempts only)."""

    exam = get_object_or_404(Exam, id=exam_id)

    attempts = (
        Attempt.objects.filter(exam=exam, is_submitted=True)
        .select_related('student')
        .order_by('-score', 'student__username')[:50]
    )

    total_marks = exam.total_marks() or 1
    rows = []
    for rank, attempt in enumerate(attempts, start=1):
        percentage = round((attempt.score / total_marks) * 100, 2)
        full_name = attempt.student.get_full_name() or attempt.student.username
        rows.append({
            'rank': rank,
            'student': attempt.student,
            'display_name': full_name,
            'score': attempt.score,
            'percentage': percentage,
            'end_time': attempt.end_time,
        })

    return render(request, 'exams/exam_leaderboard.html', {
        'exam': exam,
        'rows': rows,
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
            send_exam_completed_email(attempt)
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
        send_exam_completed_email(attempt)
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


@login_required
def review_exam(request, exam_id):
    """Review all answers before final submission"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)

    try:
        attempt = Attempt.objects.get(student=request.user, exam=exam)
    except Attempt.DoesNotExist:
        messages.error(request, 'No active attempt found. Please start the exam first.')
        return redirect('student:exam_detail', exam_id=exam.id)

    if attempt.is_submitted:
        return redirect('results:result_detail', attempt_id=attempt.id)

    questions = list(exam.questions.all())
    # Map question -> selected choice
    answers_by_qid = {a.question_id: a.selected_choice for a in attempt.answers.select_related('selected_choice', 'question')}

    questions_with_answers = [
        {
            'question': q,
            'selected_choice': answers_by_qid.get(q.id),
        }
        for q in questions
    ]

    return render(request, 'exams/review_exam.html', {
        'exam': exam,
        'attempt': attempt,
        'questions_with_answers': questions_with_answers,
    })


@require_POST
@login_required
def save_answer(request, exam_id):
    """Save a single answer via AJAX during an active attempt"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)

    try:
        attempt = Attempt.objects.get(student=request.user, exam=exam)
    except Attempt.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'No active attempt found'})

    if attempt.is_submitted:
        return JsonResponse({'success': False, 'error': 'Exam already submitted'})

    # Parse JSON body
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


@require_POST
@login_required
def submit_exam(request, exam_id):
    """Finalize an exam attempt and calculate score"""
    exam = get_object_or_404(Exam, id=exam_id, is_published=True)

    try:
        attempt = Attempt.objects.get(student=request.user, exam=exam)
    except Attempt.DoesNotExist:
        messages.error(request, 'No active attempt found. Please start the exam first.')
        return redirect('student:exam_detail', exam_id=exam.id)

    if attempt.is_submitted:
        messages.info(request, 'This exam has already been submitted.')
        return redirect('results:result_detail', attempt_id=attempt.id)

    # Finalize attempt
    attempt.is_submitted = True
    attempt.end_time = timezone.now()
    attempt.calculate_score()
    send_exam_completed_email(attempt)

    messages.success(request, 'Exam submitted successfully!')
    return redirect('results:result_detail', attempt_id=attempt.id)
