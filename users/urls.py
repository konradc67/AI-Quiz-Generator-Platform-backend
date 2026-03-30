from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView
from . import views

urlpatterns = [
    path("", views.user, name="user"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("profile/", views.profile, name="profile")
]