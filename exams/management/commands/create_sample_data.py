from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from exams.models import Exam, Question, Choice


class Command(BaseCommand):
    help = 'Create sample data for testing the exam platform'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(f'Created admin user: admin/admin123')
        
        # Create test student
        if not User.objects.filter(username='student').exists():
            student = User.objects.create_user(
                username='student',
                email='student@example.com',
                password='student123'
            )
            self.stdout.write(f'Created student user: student/student123')
        
        # Create sample exam
        if not Exam.objects.filter(title='Sample Python Quiz').exists():
            exam = Exam.objects.create(
                title='Sample Python Quiz',
                description='A sample quiz to test basic Python knowledge. This exam covers fundamental concepts including data types, control structures, and basic programming concepts.',
                duration_minutes=30,
                start_time=timezone.now() - timedelta(hours=1),
                end_time=timezone.now() + timedelta(days=7),
                is_published=True
            )
            
            # Question 1
            q1 = Question.objects.create(
                exam=exam,
                text='Which of the following is the correct way to create a list in Python?',
                marks=1
            )
            Choice.objects.create(question=q1, text='list = []', is_correct=True)
            Choice.objects.create(question=q1, text='list = ()', is_correct=False)
            Choice.objects.create(question=q1, text='list = {}', is_correct=False)
            Choice.objects.create(question=q1, text='list = <>', is_correct=False)
            
            # Question 2
            q2 = Question.objects.create(
                exam=exam,
                text='What is the output of print(2 ** 3) in Python?',
                marks=1
            )
            Choice.objects.create(question=q2, text='6', is_correct=False)
            Choice.objects.create(question=q2, text='8', is_correct=True)
            Choice.objects.create(question=q2, text='9', is_correct=False)
            Choice.objects.create(question=q2, text='23', is_correct=False)
            
            # Question 3
            q3 = Question.objects.create(
                exam=exam,
                text='Which Python keyword is used to define a function?',
                marks=1
            )
            Choice.objects.create(question=q3, text='function', is_correct=False)
            Choice.objects.create(question=q3, text='def', is_correct=True)
            Choice.objects.create(question=q3, text='define', is_correct=False)
            Choice.objects.create(question=q3, text='func', is_correct=False)
            
            # Question 4
            q4 = Question.objects.create(
                exam=exam,
                text='What data type is the result of: type("Hello World")?',
                marks=1
            )
            Choice.objects.create(question=q4, text='str', is_correct=True)
            Choice.objects.create(question=q4, text='string', is_correct=False)
            Choice.objects.create(question=q4, text='text', is_correct=False)
            Choice.objects.create(question=q4, text='char', is_correct=False)
            
            # Question 5
            q5 = Question.objects.create(
                exam=exam,
                text='Which of the following is used to add an element to the end of a list?',
                marks=1
            )
            Choice.objects.create(question=q5, text='add()', is_correct=False)
            Choice.objects.create(question=q5, text='append()', is_correct=True)
            Choice.objects.create(question=q5, text='insert()', is_correct=False)
            Choice.objects.create(question=q5, text='push()', is_correct=False)
            
            self.stdout.write(f'Created sample exam: {exam.title} with 5 questions')
        
        # Create another exam (Draft)
        if not Exam.objects.filter(title='Advanced Django Concepts').exists():
            exam2 = Exam.objects.create(
                title='Advanced Django Concepts',
                description='An advanced exam covering Django ORM, views, templates, and best practices.',
                duration_minutes=45,
                start_time=timezone.now() + timedelta(hours=2),
                end_time=timezone.now() + timedelta(days=10),
                is_published=False  # Draft exam
            )
            
            # Question 1 for Django exam
            q1 = Question.objects.create(
                exam=exam2,
                text='Which Django ORM method is used to get a single object?',
                marks=2
            )
            Choice.objects.create(question=q1, text='get()', is_correct=True)
            Choice.objects.create(question=q1, text='filter()', is_correct=False)
            Choice.objects.create(question=q1, text='all()', is_correct=False)
            Choice.objects.create(question=q1, text='first()', is_correct=False)
            
            self.stdout.write(f'Created draft exam: {exam2.title}')
        
        self.stdout.write(
            self.style.SUCCESS('Sample data created successfully!')
        )
        self.stdout.write('Login credentials:')
        self.stdout.write('Admin: admin/admin123')
        self.stdout.write('Student: student/student123')