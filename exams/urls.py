from django.urls import path
from . import views

app_name = 'student'

urlpatterns = [
    path('', views.student_dashboard, name='dashboard'),
    path('profile/', views.student_profile, name='profile'),
    path('leaderboard/', views.global_leaderboard, name='global_leaderboard'),
    path('exam/<int:exam_id>/leaderboard/', views.exam_leaderboard, name='exam_leaderboard'),
    path('exam/<int:exam_id>/', views.exam_detail, name='exam_detail'),
    path('exam/<int:exam_id>/start/', views.start_exam, name='start_exam'),
    path('exam/<int:exam_id>/take/', views.take_exam, name='take_exam'),
    path('exam/<int:exam_id>/review/', views.review_exam, name='review_exam'),
    path('exam/<int:exam_id>/save-answer/', views.save_answer, name='save_answer'),
    path('exam/<int:exam_id>/submit/', views.submit_exam, name='submit_exam'),
]