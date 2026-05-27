from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/',views.register, name='register'),
    path('auth/login/',views.login, name='login'),
    path('auth/logout/',views.logout, name='logout'),
    
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:pk>/', views.project_detail, name='project_detail'),
    
    path('projects/<int:project_pk>/tasks/',views.task_list, name='task_list'),
    path('projects/<int:project_pk>/tasks/<int:pk>/',views.task_detail, name='task_detail'),
    
    path('projects/<int:project_pk>/summary/', views.project_summary, name='project_summary')
]
