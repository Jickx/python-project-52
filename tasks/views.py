from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.utils.translation import gettext_lazy as _

from .models import Task

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/list.html'
    context_object_name = 'tasks'

class TaskDetailView(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'tasks/detail.html'
    context_object_name = 'task'

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    fields = ['name', 'description', 'status', 'executor']
    template_name = 'tasks/create.html'
    success_url = reverse_lazy('tasks:list')
    # Disallow PUT (tests expect 405)
    http_method_names = ['get', 'post', 'head', 'options']

    def form_valid(self, form):
        form.instance.author = self.request.user
        messages.success(self.request, _('Task created successfully'))
        return super().form_valid(form)

class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['name', 'description', 'status', 'executor']
    template_name = 'tasks/update.html'
    success_url = reverse_lazy('tasks:list')
    # Disallow PUT (tests expect 405)
    http_method_names = ['get', 'post', 'head', 'options']

    def form_valid(self, form):
        messages.success(self.request, _('Task updated successfully'))
        return super().form_valid(form)

class AuthorRequiredMixin(UserPassesTestMixin):
    """Only the task author can access the view (authenticated users only)."""

    def test_func(self):
        # If user isn't authenticated, let LoginRequiredMixin handle redirect to login
        if not self.request.user.is_authenticated:
            return True
        task = self.get_object()
        return task.author == self.request.user

    def handle_no_permission(self):
        # If not authenticated, delegate to standard behavior (login redirect)
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, _('Only the author can delete this task'))
        return redirect('tasks:list')

class TaskDeleteView(LoginRequiredMixin, AuthorRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks:list')
    http_method_names = ['get', 'post', 'head', 'options']

    def post(self, request, *args, **kwargs):
        messages.success(request, _('Task deleted successfully'))
        return super().post(request, *args, **kwargs)
