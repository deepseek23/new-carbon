from django.contrib import admin
from django.urls import path
from . import views

app_name = 'challenges'

urlpatterns = [
    path('', views.index, name='index'),
    path('join/<int:challenge_id>/', views.join_challenge, name='join_challenge'),
    path('my-challenges/', views.my_challenges, name='my_challenges'),
    path('update-progress/<int:challenge_id>/', views.update_progress, name='update_progress'),
]