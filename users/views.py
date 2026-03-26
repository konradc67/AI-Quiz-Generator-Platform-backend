from django.shortcuts import render
from django.http import HttpResponse

def login(request):
    return HttpResponse("Login page")

def user(request):
    return HttpResponse("user page")

def register(request):
    return HttpResponse("register page")

def profile(request):
    return HttpResponse("profile page")