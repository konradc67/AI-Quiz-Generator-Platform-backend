from . import views
from django.contrib import admin
from django.urls import path, include
from .views import QuizGenerateView, QuizHistoryView, QuizDetailView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("user/", include('users.urls')),
    path("generate/", QuizGenerateView.as_view(), name='quiz-generate'),
    path("history/", QuizHistoryView.as_view(), name='quiz-history'),
    path("history/<int:quiz_id>/", QuizDetailView.as_view(), name='quiz-detail')
]