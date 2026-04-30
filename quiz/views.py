from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import get_ai_quiz

def home(request):
    return render(request, 'quiz/home.html')

class QuizGenerateView(APIView):
    def post(self, request):
        topic = request.data.get('prompt')
        question_count = request.data.get('questionCount', 10)
        difficulty = request.data.get('difficulty', 'medium')

        if not topic:
             return Response({"error": "Prompt jest wymagany."}, status=status.HTTP_400_BAD_REQUEST)

        ai_data = get_ai_quiz(topic, question_count, difficulty)
        
        if isinstance(ai_data, dict) and "error" in ai_data:
            return Response(ai_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({"questions": ai_data}, status=status.HTTP_200_OK)