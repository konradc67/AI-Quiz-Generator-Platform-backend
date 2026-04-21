from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from .utils import get_ai_quiz

def home(request):
    return render(request, 'quiz/home.html')

class QuizGenerateView(APIView):
    def post(self, request):
        topic = request.data.get('topic', 'General Knowledge')
        ai_data = get_ai_quiz(topic)
        return Response(ai_data)