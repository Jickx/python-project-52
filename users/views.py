from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import ProtectedError
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.shortcuts import redirect

from .forms import UserRegistrationForm, UserUpdateForm


class UserListView(ListView):
    model = User
    template_name = 'users/list.html'
    context_object_name = 'users'


class UserCreateView(SuccessMessageMixin, CreateView):
    model = User
    form_class = UserRegistrationForm
    template_name = 'users/create.html'
    success_url = reverse_lazy('home')  # Изменить на главную страницу
    success_message = _('User successfully registered')

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Автоматический вход
        return response

    def form_invalid(self, form):
        # Явно вернуть форму с ошибками (например, при несовпадении паролей)
        return self.render_to_response(self.get_context_data(form=form))


class UserUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = User
    form_class = UserUpdateForm
    template_name = 'users/update.html'
    success_url = reverse_lazy('users:list')
    success_message = _('User successfully updated')

    def dispatch(self, request, *args, **kwargs):
        # If not authenticated, let LoginRequiredMixin redirect to login with ?next=
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        # Authenticated: allow only editing own profile
        if self.get_object() != request.user:
            messages.error(request, _('You can only edit your own profile'))
            return redirect('users:list')
        return super().dispatch(request, *args, **kwargs)


class UserDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/delete.html'
    success_url = reverse_lazy('users:list')

    def dispatch(self, request, *args, **kwargs):
        # If not authenticated, let LoginRequiredMixin redirect to login with ?next=
        if not request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        # Authenticated: allow only deleting own profile
        if self.get_object() != request.user:
            messages.error(request, _('You can only delete your own profile'))
            return redirect('users:list')
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        try:
            user.delete()
            messages.success(request, _('User successfully deleted'))
        except ProtectedError:
            messages.error(request, _('User cannot be deleted due to related data'))
        finally:
            logout(request)
        return redirect(self.success_url)
