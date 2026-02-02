from django.urls import path
from . import views

app_name = 'attempts'

urlpatterns = [
    path('save-answer/', views.save_answer, name='save_answer'),
]