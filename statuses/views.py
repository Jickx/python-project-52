from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import ProtectedError
from django.shortcuts import redirect

from .models import Status
from .forms import StatusForm

class StatusListView(LoginRequiredMixin, ListView):
    model = Status
    template_name = 'statuses/list.html'
    context_object_name = 'statuses'

class StatusCreateView(LoginRequiredMixin, CreateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/create.html'
    success_url = reverse_lazy('statuses:list')

    def form_valid(self, form):
        messages.success(self.request, _('Status created successfully'))
        return super().form_valid(form)

class StatusUpdateView(LoginRequiredMixin, UpdateView):
    model = Status
    form_class = StatusForm
    template_name = 'statuses/update.html'
    success_url = reverse_lazy('statuses:list')

    def form_valid(self, form):
        messages.success(self.request, _('Status updated successfully'))
        return super().form_valid(form)

class StatusDeleteView(LoginRequiredMixin, DeleteView):
    model = Status
    template_name = 'statuses/delete.html'
    success_url = reverse_lazy('statuses:list')

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            messages.success(request, _('Status deleted successfully'))
        except ProtectedError:
            messages.error(request, _('Status cannot be deleted because it is in use'))
        return redirect(self.success_url)
