from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Exam, Question, Choice, Category
from attempts.models import Attempt, Answer


class ExamModelTests(TestCase):
	def setUp(self):
		self.category = Category.objects.create(name="Math")
		now = timezone.now()
		# Active, published exam
		self.exam = Exam.objects.create(
			category=self.category,
			title="Algebra Test",
			description="Basic algebra questions",
			duration_minutes=30,
			start_time=now - timezone.timedelta(minutes=5),
			end_time=now + timezone.timedelta(minutes=25),
			is_published=True,
		)

	def test_exam_is_active_when_within_window_and_published(self):
		self.assertTrue(self.exam.is_active())

	def test_exam_not_active_when_unpublished(self):
		self.exam.is_published = False
		self.exam.save()
		self.assertFalse(self.exam.is_active())

	def test_exam_not_active_before_start_time(self):
		now = timezone.now()
		future_exam = Exam.objects.create(
			category=self.category,
			title="Future Test",
			description="",
			duration_minutes=10,
			start_time=now + timezone.timedelta(hours=1),
			end_time=now + timezone.timedelta(hours=2),
			is_published=True,
		)
		self.assertFalse(future_exam.is_active())

	def test_exam_not_active_after_end_time(self):
		now = timezone.now()
		past_exam = Exam.objects.create(
			category=self.category,
			title="Past Test",
			description="",
			duration_minutes=10,
			start_time=now - timezone.timedelta(hours=2),
			end_time=now - timezone.timedelta(hours=1),
			is_published=True,
		)
		self.assertFalse(past_exam.is_active())


class AttemptScoreTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="student", password="test123")
		now = timezone.now()
		self.exam = Exam.objects.create(
			title="Scoring Test",
			description="",
			duration_minutes=30,
			start_time=now - timezone.timedelta(minutes=5),
			end_time=now + timezone.timedelta(minutes=25),
			is_published=True,
		)
		# Two questions, different marks
		q1 = Question.objects.create(exam=self.exam, text="Q1", marks=1)
		q2 = Question.objects.create(exam=self.exam, text="Q2", marks=2)

		self.q1_correct = Choice.objects.create(question=q1, text="A", is_correct=True)
		self.q1_wrong = Choice.objects.create(question=q1, text="B", is_correct=False)

		self.q2_correct = Choice.objects.create(question=q2, text="X", is_correct=True)
		self.q2_wrong = Choice.objects.create(question=q2, text="Y", is_correct=False)

		self.attempt = Attempt.objects.create(
			student=self.user,
			exam=self.exam,
			start_time=now,
		)

	def test_calculate_score_counts_only_correct_answers_with_marks(self):
		# Q1 answered correctly, Q2 answered incorrectly
		Answer.objects.create(attempt=self.attempt, question=self.q1_correct.question, selected_choice=self.q1_correct)
		Answer.objects.create(attempt=self.attempt, question=self.q2_correct.question, selected_choice=self.q2_wrong)

		score = self.attempt.calculate_score()
		self.assertEqual(score, 1)
		self.assertEqual(self.attempt.score, 1)

	def test_calculate_score_full_marks_when_all_correct(self):
		Answer.objects.create(attempt=self.attempt, question=self.q1_correct.question, selected_choice=self.q1_correct)
		Answer.objects.create(attempt=self.attempt, question=self.q2_correct.question, selected_choice=self.q2_correct)

		score = self.attempt.calculate_score()
		self.assertEqual(score, 3)
		self.assertEqual(self.attempt.score, 3)

