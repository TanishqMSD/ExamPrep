"""
URL configuration for examprep project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth.views import LogoutView
from core.views import HomeView, PastPaperListView, QuizListView, ProgressView, NoteListView, RegisterView, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HomeView.as_view(), name='home'),
    path('past-papers/', PastPaperListView.as_view(), name='past_papers'),
    path('quizzes/', QuizListView.as_view(), name='quizzes'),
    path('progress/', ProgressView.as_view(), name='progress'),
    path('notes/', NoteListView.as_view(), name='notes'),
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),
]
