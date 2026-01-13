from django.urls import path
from .views import (
    TaskListView,
    TaskCreateView,
    TaskUpdateView,
    TaskDeleteView,
    TaskDetailView,
)

app_name = 'tasks'

urlpatterns = [
    path('', TaskListView.as_view(), name='list'),                     # GET /tasks/
    path('create/', TaskCreateView.as_view(), name='create'),          # GET/POST /tasks/create/
    path('<int:pk>/update/', TaskUpdateView.as_view(), name='update'), # GET/POST /tasks/<pk>/update/
    path('<int:pk>/delete/', TaskDeleteView.as_view(), name='delete'), # GET/POST /tasks/<pk>/delete/
    path('<int:pk>/', TaskDetailView.as_view(), name='detail'),        # GET /tasks/<pk>/
]
