from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('past-papers/', views.PastPaperListView.as_view(), name='past_papers'),
    path('quizzes/', views.QuizListView.as_view(), name='quizzes'),
    path('progress/', views.ProgressView.as_view(), name='progress'),
    path('notes/', views.NoteListView.as_view(), name='notes'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
]