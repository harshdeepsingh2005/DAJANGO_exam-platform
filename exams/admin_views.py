from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.forms import formset_factory
from django.utils import timezone
from django.contrib.auth.models import User
from django.http import JsonResponse

from .models import Exam, Question, Choice
from .forms import ExamForm, QuestionForm, ChoiceForm
from attempts.models import Attempt


def is_staff(user):
    """Check if user is staff/admin"""
    return user.is_authenticated and user.is_staff


@user_passes_test(is_staff)
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    total_students = User.objects.filter(is_staff=False).count()
    total_exams = Exam.objects.count()
    total_attempts = Attempt.objects.count()
    
    recent_attempts = Attempt.objects.select_related('student', 'exam').order_by('-created_at')[:10]
    
    context = {
        'total_students': total_students,
        'total_exams': total_exams,
        'total_attempts': total_attempts,
        'recent_attempts': recent_attempts,
    }
    
    return render(request, 'admin/dashboard.html', context)


@user_passes_test(is_staff)
def admin_exam_list(request):
    """List all exams for admin"""
    exams = Exam.objects.all().order_by('-created_at')
    return render(request, 'admin/exam_list.html', {'exams': exams})


@user_passes_test(is_staff)
def admin_exam_create(request):
    """Create new exam"""
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f'Exam "{exam.title}" created successfully!')
            return redirect('admin-panel:question_list', exam_id=exam.id)
    else:
        form = ExamForm()
    
    return render(request, 'admin/exam_form.html', {'form': form, 'title': 'Create Exam'})


@user_passes_test(is_staff)
def admin_exam_edit(request, exam_id):
    """Edit existing exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=exam)
        if form.is_valid():
            exam = form.save()
            messages.success(request, f'Exam "{exam.title}" updated successfully!')
            return redirect('admin-panel:exam_list')
    else:
        form = ExamForm(instance=exam)
    
    return render(request, 'admin/exam_form.html', {
        'form': form, 
        'title': 'Edit Exam',
        'exam': exam
    })


@user_passes_test(is_staff)
def admin_question_list(request, exam_id):
    """List questions for an exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all().order_by('id')
    
    return render(request, 'admin/question_list.html', {
        'exam': exam,
        'questions': questions
    })


@user_passes_test(is_staff)
def admin_question_create(request, exam_id):
    """Create new question for exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    
    # Create formset for choices (4 choices)
    ChoiceFormSet = formset_factory(ChoiceForm, extra=4, min_num=4, max_num=4)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST)
        choice_formset = ChoiceFormSet(request.POST)
        
        if question_form.is_valid() and choice_formset.is_valid():
            # Save question
            question = question_form.save(commit=False)
            question.exam = exam
            question.save()
            
            # Save choices
            correct_choices = 0
            for choice_form in choice_formset:
                if choice_form.cleaned_data:
                    choice = choice_form.save(commit=False)
                    choice.question = question
                    choice.save()
                    if choice.is_correct:
                        correct_choices += 1
            
            # Validate that exactly one choice is correct
            if correct_choices != 1:
                question.delete()  # Rollback
                messages.error(request, 'Exactly one choice must be marked as correct!')
            else:
                messages.success(request, 'Question created successfully!')
                return redirect('admin-panel:question_list', exam_id=exam.id)
    else:
        question_form = QuestionForm()
        choice_formset = ChoiceFormSet()
    
    return render(request, 'admin/question_form.html', {
        'exam': exam,
        'question_form': question_form,
        'choice_formset': choice_formset,
        'title': 'Create Question'
    })


@user_passes_test(is_staff)
def admin_question_edit(request, question_id):
    """Edit existing question"""
    question = get_object_or_404(Question, id=question_id)
    exam = question.exam
    
    # Create formset for choices
    ChoiceFormSet = formset_factory(ChoiceForm, extra=0)
    
    if request.method == 'POST':
        question_form = QuestionForm(request.POST, instance=question)
        choice_formset = ChoiceFormSet(request.POST)
        
        if question_form.is_valid() and choice_formset.is_valid():
            question = question_form.save()
            
            # Delete existing choices
            question.choices.all().delete()
            
            # Save new choices
            correct_choices = 0
            for choice_form in choice_formset:
                if choice_form.cleaned_data and choice_form.cleaned_data.get('text'):
                    choice = choice_form.save(commit=False)
                    choice.question = question
                    choice.save()
                    if choice.is_correct:
                        correct_choices += 1
            
            # Validate that exactly one choice is correct
            if correct_choices != 1:
                messages.error(request, 'Exactly one choice must be marked as correct!')
            else:
                messages.success(request, 'Question updated successfully!')
                return redirect('admin-panel:question_list', exam_id=exam.id)
    else:
        question_form = QuestionForm(instance=question)
        initial_data = [{'text': choice.text, 'is_correct': choice.is_correct} 
                       for choice in question.choices.all()]
        # Pad to 4 choices
        while len(initial_data) < 4:
            initial_data.append({'text': '', 'is_correct': False})
        choice_formset = ChoiceFormSet(initial=initial_data)
    
    return render(request, 'admin/question_form.html', {
        'exam': exam,
        'question': question,
        'question_form': question_form,
        'choice_formset': choice_formset,
        'title': 'Edit Question'
    })


@user_passes_test(is_staff)
def admin_attempt_list(request, exam_id):
    """List attempts for an exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    attempts = Attempt.objects.filter(exam=exam).select_related('student').order_by('-created_at')
    
    return render(request, 'admin/attempt_list.html', {
        'exam': exam,
        'attempts': attempts
    })


@user_passes_test(is_staff)
def admin_toggle_publish(request, exam_id):
    """Toggle exam publish status"""
    exam = get_object_or_404(Exam, id=exam_id)
    exam.is_published = not exam.is_published
    exam.save()
    
    status = 'published' if exam.is_published else 'unpublished'
    messages.success(request, f'Exam "{exam.title}" has been {status}.')
    
    return redirect('admin-panel:exam_list')