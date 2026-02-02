from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.models import Group


STUDENT_GROUP_NAME = 'Student'


def _get_from_email() -> str:
    """Return a safe from-email address."""
    return getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@example.com')


def send_exam_published_email(exam):
    """Notify all students that a new exam has been published.

    This uses the Student group; if the group does not exist or there are
    no recipients with an email address, it quietly does nothing.
    """
    try:
        student_group = Group.objects.get(name=STUDENT_GROUP_NAME)
    except Group.DoesNotExist:
        return

    recipients = list(
        student_group.user_set.exclude(email='').values_list('email', flat=True)
    )

    if not recipients:
        return

    subject = f"New exam published: {exam.title}"
    lines = [
        f"A new exam has been published on NovaExam.",
        "",
        f"Title: {exam.title}",
    ]
    if exam.category:
        lines.append(f"Category: {exam.category.name}")
    if exam.start_time and exam.end_time:
        lines.append(f"Available: {exam.start_time} to {exam.end_time}")

    lines.append("")
    lines.append("You can view available exams from your dashboard.")

    message = "\n".join(lines)

    send_mail(
        subject,
        message,
        _get_from_email(),
        recipients,
        fail_silently=True,
    )


def send_exam_completed_email(attempt):
    """Send a confirmation + brief summary when a student completes an exam."""
    student = attempt.student
    if not student.email:
        return

    exam = attempt.exam
    total_questions = exam.total_questions()
    total_marks = exam.total_marks()
    score = attempt.score or 0
    percentage = (score / total_marks * 100) if total_marks else 0
    passed = percentage >= 60

    subject = f"Exam completed: {exam.title}"

    lines = [
        f"Hi {student.username},",
        "",
        "You have successfully completed the following exam:",
        f"Title: {exam.title}",
        "",
        f"Score: {score} / {total_marks}",
        f"Percentage: {percentage:.2f}%",
        f"Status: {'PASSED' if passed else 'FAILED'}",
    ]

    if exam.category:
        lines.append(f"Category: {exam.category.name}")

    lines.append("")
    lines.append("You can view full details and explanations from your results page in the portal.")

    message = "\n".join(lines)

    send_mail(
        subject,
        message,
        _get_from_email(),
        [student.email],
        fail_silently=True,
    )
