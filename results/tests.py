from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

from exams.models import Exam, Question, Choice
from attempts.models import Attempt, Answer


class ResultViewTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="student", password="test123")
		now = timezone.now()
		self.exam = Exam.objects.create(
			title="Result Test",
			description="",
			duration_minutes=10,
			start_time=now - timezone.timedelta(minutes=5),
			end_time=now + timezone.timedelta(minutes=5),
			is_published=True,
		)
		self.question = Question.objects.create(exam=self.exam, text="Q1", marks=2)
		self.correct_choice = Choice.objects.create(question=self.question, text="A", is_correct=True)
		self.wrong_choice = Choice.objects.create(question=self.question, text="B", is_correct=False)

		self.attempt = Attempt.objects.create(
			student=self.user,
			exam=self.exam,
			start_time=now - timezone.timedelta(minutes=1),
			end_time=now,
			is_submitted=True,
		)
		Answer.objects.create(attempt=self.attempt, question=self.question, selected_choice=self.correct_choice)
		# Calculate score once to mirror real flow
		self.attempt.calculate_score()

	def test_result_detail_requires_login_and_own_attempt(self):
		url = reverse('results:result_detail', args=[self.attempt.id])

		# Anonymous should be redirected to login
		response = self.client.get(url)
		self.assertEqual(response.status_code, 302)
		self.assertIn('/accounts/login/', response['Location'])

		# Logged-in student can view their own result
		self.client.login(username='student', password='test123')
		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertContains(response, "Result Test")
		self.assertContains(response, "Q1")

