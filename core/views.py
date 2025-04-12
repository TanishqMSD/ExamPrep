from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.views import View
from django.http import JsonResponse
from .models import PastPaper, Quiz, Progress, Note

class HomeView(TemplateView):
    template_name = 'core/home.html'

class PastPaperListView(ListView):
    model = PastPaper
    template_name = 'core/past_papers.html'
    context_object_name = 'papers'

class QuizListView(ListView):
    model = Quiz
    template_name = 'core/quizzes.html'
    context_object_name = 'quizzes'

class ProgressView(LoginRequiredMixin, TemplateView):
    template_name = 'core/progress.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['progress'] = Progress._default_manager.filter(user=self.request.user)
        return context

class NoteListView(LoginRequiredMixin, ListView):
    model = Note
    template_name = 'core/notes.html'
    context_object_name = 'notes'
    
    def get_queryset(self):
        return Note._default_manager.filter(user=self.request.user)

class RegisterView(View):
    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, 'core/register.html', {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        return render(request, 'core/register.html', {'form': form})

class LoginView(View):
    def get(self, request):
        return render(request, 'core/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        return render(request, 'core/login.html', {'form': {'errors': True}})
