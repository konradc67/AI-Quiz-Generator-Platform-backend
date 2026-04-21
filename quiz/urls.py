from . import views
from django.contrib import admin
from django.urls import path, include
from .views import QuizGenerateView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("user/", include('users.urls')),
    path("generate/", QuizGenerateView.as_view(), name='quiz-generate')
]