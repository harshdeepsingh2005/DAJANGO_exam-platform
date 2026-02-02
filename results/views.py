from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from attempts.models import Attempt


@login_required
def result_detail(request, attempt_id):
    """Show exam results to student"""
    attempt = get_object_or_404(Attempt, id=attempt_id, student=request.user)
    
    if not attempt.is_submitted:
        # If somehow they access this without submitting, redirect to exam
        from django.shortcuts import redirect
        return redirect('student:take_exam', exam_id=attempt.exam.id)
    
    # Calculate statistics
    total_questions = attempt.exam.total_questions()
    total_marks = attempt.exam.total_marks()
    correct_answers = 0
    
    for answer in attempt.answers.all():
        if answer.selected_choice and answer.selected_choice.is_correct:
            correct_answers += 1
    
    percentage = (attempt.score / total_marks * 100) if total_marks > 0 else 0
    passed = percentage >= 60  # 60% pass criteria
    
    context = {
        'attempt': attempt,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'total_marks': total_marks,
        'percentage': round(percentage, 2),
        'passed': passed,
    }
    
    return render(request, 'results/result_detail.html', context)
