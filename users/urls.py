from . import views
from django.urls import path

urlpatterns = [
    path("", views.user),
    path("login/", views.login, name="login"),
    path("register/", views.register, name="register"),
    path("profile/", views.profile, name="profile")
]
