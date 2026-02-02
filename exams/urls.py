from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('', views.student_dashboard, name='dashboard'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:exam_id>/start/', views.start_exam, name='start_exam'),
    path('exam/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
]