from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import IntegrityError

from exams.models import Exam
from .models import Attempt


class AttemptModelTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username="student", password="test123")
		now = timezone.now()
		self.exam = Exam.objects.create(
			title="Timing Test",
			description="",
			duration_minutes=30,
			start_time=now - timezone.timedelta(minutes=5),
			end_time=now + timezone.timedelta(minutes=25),
			is_published=True,
		)

	def test_one_attempt_per_exam_enforced(self):
		now = timezone.now()
		Attempt.objects.create(student=self.user, exam=self.exam, start_time=now)

		with self.assertRaises(IntegrityError):
			Attempt.objects.create(student=self.user, exam=self.exam, start_time=now)

	def test_is_expired_respects_exam_duration(self):
		now = timezone.now()
		attempt = Attempt.objects.create(
			student=self.user,
			exam=self.exam,
			start_time=now - timezone.timedelta(minutes=self.exam.duration_minutes + 1),
		)
		self.assertTrue(attempt.is_expired())

	def test_time_remaining_zero_when_submitted(self):
		now = timezone.now()
		attempt = Attempt.objects.create(
			student=self.user,
			exam=self.exam,
			start_time=now,
			is_submitted=True,
		)
		self.assertEqual(attempt.time_remaining(), 0)

