from django.urls import path
from . import views

app_name = 'results'

urlpatterns = [
    path('result/<int:attempt_id>/', views.result_detail, name='result_detail'),
]