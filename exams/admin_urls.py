from django.urls import path
from . import admin_views

app_name = 'admin-panel'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('exams/', admin_views.admin_exam_list, name='exam_list'),
    path('exams/create/', admin_views.admin_exam_create, name='exam_create'),
    path('exams/<int:exam_id>/edit/', admin_views.admin_exam_edit, name='exam_edit'),
    path('exams/<int:exam_id>/stats/', admin_views.admin_exam_stats, name='exam_stats'),
    path('exams/<int:exam_id>/questions/', admin_views.admin_question_list, name='question_list'),
    path('exams/<int:exam_id>/questions/create/', admin_views.admin_question_create, name='question_create'),
    path('exams/<int:exam_id>/questions/bulk-upload/', admin_views.admin_question_bulk_upload, name='question_bulk_upload'),
    path('questions/<int:question_id>/edit/', admin_views.admin_question_edit, name='question_edit'),
    path('exams/<int:exam_id>/attempts/', admin_views.admin_attempt_list, name='attempt_list'),
    path('exams/<int:exam_id>/toggle-publish/', admin_views.admin_toggle_publish, name='toggle_publish'),
]