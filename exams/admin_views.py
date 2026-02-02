from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.forms import formset_factory
from django.utils import timezone
from django.contrib.auth.models import User, Group
from django.http import JsonResponse
import csv
from io import StringIO, TextIOWrapper

from .models import Exam, Question, Choice, Category
from .forms import ExamForm, QuestionForm, ChoiceForm, QuestionBulkUploadForm
from .email_utils import send_exam_published_email
from attempts.models import Attempt, Answer


EXAM_ADMIN_GROUP = 'ExamAdmin'


def is_exam_admin(user):
    """Check if user has exam admin privileges"""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name=EXAM_ADMIN_GROUP).exists()


@user_passes_test(is_exam_admin)
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


@user_passes_test(is_exam_admin)
def admin_exam_list(request):
    """List all exams for admin"""
    exams = Exam.objects.all().order_by('-created_at')

    category_id = request.GET.get('category')
    if category_id:
        exams = exams.filter(category_id=category_id)

    categories = Category.objects.all()

    return render(request, 'admin/exam_list.html', {
        'exams': exams,
        'categories': categories,
        'selected_category_id': category_id,
    })


@user_passes_test(is_exam_admin)
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


@user_passes_test(is_exam_admin)
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


@user_passes_test(is_exam_admin)
def admin_question_list(request, exam_id):
    """List questions for an exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    questions = exam.questions.all().order_by('id')
    
    return render(request, 'admin/question_list.html', {
        'exam': exam,
        'questions': questions
    })


@user_passes_test(is_exam_admin)
def admin_question_bulk_upload(request, exam_id):
    """Bulk upload questions for an exam from a CSV file.

    Expected CSV columns (header row required):
    - question (text)
    - option1, option2, option3, option4
    - correct (1-4 or exact option text)
    - marks (optional, default 1)
    - explanation (optional)
    - time_limit_seconds (optional integer)
    """

    exam = get_object_or_404(Exam, id=exam_id)

    if request.method == 'POST':
        form = QuestionBulkUploadForm(request.POST, request.FILES)
        if form.is_valid():
            upload = form.cleaned_data['file']
            clear_existing = form.cleaned_data['clear_existing']

            # Decode uploaded file
            try:
                if isinstance(upload, TextIOWrapper):
                    text = upload.read()
                else:
                    text = upload.read().decode('utf-8')
            except Exception:
                messages.error(request, 'Could not read the uploaded file. Please ensure it is a UTF-8 encoded CSV.')
                return redirect('admin-panel:question_bulk_upload', exam_id=exam.id)

            reader = csv.DictReader(StringIO(text))
            required_columns = {'question', 'option1', 'option2', 'option3', 'option4', 'correct'}
            missing = required_columns - set(reader.fieldnames or [])
            if missing:
                messages.error(request, f'Missing required columns in CSV: {", ".join(sorted(missing))}')
                return redirect('admin-panel:question_bulk_upload', exam_id=exam.id)

            if clear_existing:
                exam.questions.all().delete()

            created = 0
            skipped = 0

            for idx, row in enumerate(reader, start=2):  # start=2 accounts for header
                question_text = (row.get('question') or '').strip()
                if not question_text:
                    skipped += 1
                    continue

                options = [
                    (row.get('option1') or '').strip(),
                    (row.get('option2') or '').strip(),
                    (row.get('option3') or '').strip(),
                    (row.get('option4') or '').strip(),
                ]

                if not all(options):
                    skipped += 1
                    continue

                correct_raw = (row.get('correct') or '').strip()
                correct_index = None

                if correct_raw.isdigit():
                    num = int(correct_raw)
                    if 1 <= num <= 4:
                        correct_index = num - 1
                else:
                    # Try to match by option text (case-insensitive)
                    lower_options = [o.lower() for o in options]
                    try:
                        correct_index = lower_options.index(correct_raw.lower())
                    except ValueError:
                        correct_index = None

                if correct_index is None:
                    skipped += 1
                    continue

                marks_raw = (row.get('marks') or '').strip()
                try:
                    marks = int(marks_raw) if marks_raw else 1
                except ValueError:
                    marks = 1

                explanation = (row.get('explanation') or '').strip()
                tls_raw = (row.get('time_limit_seconds') or '').strip()
                time_limit_seconds = None
                if tls_raw:
                    try:
                        time_limit_seconds = int(tls_raw)
                    except ValueError:
                        time_limit_seconds = None

                # Create question
                question = Question.objects.create(
                    exam=exam,
                    text=question_text,
                    marks=marks,
                    explanation=explanation,
                    time_limit_seconds=time_limit_seconds,
                )

                # Create choices
                for i, opt_text in enumerate(options):
                    Choice.objects.create(
                        question=question,
                        text=opt_text,
                        is_correct=(i == correct_index),
                    )

                created += 1

            messages.success(
                request,
                f'Imported {created} question(s) for "{exam.title}". Skipped {skipped} row(s) due to missing/invalid data.'
            )
            return redirect('admin-panel:question_list', exam_id=exam.id)
    else:
        form = QuestionBulkUploadForm()

    return render(request, 'admin/question_bulk_upload.html', {
        'exam': exam,
        'form': form,
    })


@user_passes_test(is_exam_admin)
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


@user_passes_test(is_exam_admin)
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


@user_passes_test(is_exam_admin)
def admin_attempt_list(request, exam_id):
    """List attempts for an exam"""
    exam = get_object_or_404(Exam, id=exam_id)
    attempts = Attempt.objects.filter(exam=exam).select_related('student').order_by('-created_at')
    
    return render(request, 'admin/attempt_list.html', {
        'exam': exam,
        'attempts': attempts
    })


@user_passes_test(is_exam_admin)
def admin_exam_stats(request, exam_id):
    """Detailed statistics and analytics for a single exam"""
    exam = get_object_or_404(Exam, id=exam_id)

    attempts_qs = Attempt.objects.filter(exam=exam)
    submitted_attempts = attempts_qs.filter(is_submitted=True)

    total_attempts = attempts_qs.count()
    total_submitted = submitted_attempts.count()

    avg_score = None
    pass_rate = None
    if total_submitted:
        from django.db.models import Avg

        stats = submitted_attempts.aggregate(avg=Avg('score'))
        avg_score = stats['avg'] or 0

        # Passing threshold mirrors result_detail (60%)
        passing_score = exam.total_marks() * 0.6
        passed_count = submitted_attempts.filter(score__gte=passing_score).count()
        pass_rate = (passed_count / total_submitted) * 100 if total_submitted else None

    # Per-question difficulty: how many students answered correctly vs attempted
    question_stats = []
    questions = exam.questions.all().order_by('id')

    for question in questions:
        q_answers = Answer.objects.filter(attempt__exam=exam, question=question, attempt__is_submitted=True)
        attempted = q_answers.exclude(selected_choice__isnull=True).count()
        correct = q_answers.filter(selected_choice__is_correct=True).count()

        difficulty = None
        if attempted:
            difficulty = (correct / attempted) * 100

        question_stats.append({
            'question': question,
            'attempted': attempted,
            'correct': correct,
            'difficulty': difficulty,
        })

    context = {
        'exam': exam,
        'total_attempts': total_attempts,
        'total_submitted': total_submitted,
        'avg_score': avg_score,
        'pass_rate': pass_rate,
        'question_stats': question_stats,
    }

    return render(request, 'admin/exam_stats.html', context)


@user_passes_test(is_exam_admin)
def admin_toggle_publish(request, exam_id):
    """Toggle exam publish status"""
    exam = get_object_or_404(Exam, id=exam_id)
    previous_status = exam.is_published
    exam.is_published = not exam.is_published
    exam.save()
    
    status = 'published' if exam.is_published else 'unpublished'
    messages.success(request, f'Exam "{exam.title}" has been {status}.')

    # Notify students only when an exam becomes newly published
    if not previous_status and exam.is_published:
        send_exam_published_email(exam)
    
    return redirect('admin-panel:exam_list')