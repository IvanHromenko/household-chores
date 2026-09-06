from django.urls import path
from . import views

app_name = 'chores'

urlpatterns = [
    path('', views.today, name='today'),
    path('chores/', views.chore_list, name='chore_list'),
]
