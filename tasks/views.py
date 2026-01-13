from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
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

class TaskDeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    template_name = 'tasks/delete.html'
    success_url = reverse_lazy('tasks:list')
    http_method_names = ['get', 'post', 'head', 'options']

    def post(self, request, *args, **kwargs):
        messages.success(request, _('Task deleted successfully'))
        return super().post(request, *args, **kwargs)
