from django.shortcuts import render, redirect
from .forms import UserRegisterForm
from django.http import HttpResponse

def login(request):
    return HttpResponse("Login page")

def user(request):
    return HttpResponse("user page")

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm()
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'user/register.html', {'form': form})

def profile(request):
    return HttpResponse("profile page")