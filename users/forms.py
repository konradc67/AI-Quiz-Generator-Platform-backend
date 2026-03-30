from django.contrib.auth.forms import User
from django import forms
from .models import User

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email',
                    'password', 'country', 'role']
        