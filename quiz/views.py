from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .utils import get_ai_quiz, save_ai_quiz
import traceback

def home(request):
    return render(request, 'quiz/home.html')

class QuizGenerateView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            topic = request.data.get('prompt') or request.data.get('topic', 'General Knowledge')
            question_count = request.data.get('questionCount', 5)
            difficulty = request.data.get('difficulty', 'easy')
            
            ai_data = get_ai_quiz(topic, question_count, difficulty)
            
            if isinstance(ai_data, dict) and "error" in ai_data:
                return Response({"success": False, "error": ai_data}, status=400)

            quiz_id = None
            
            if request.user.is_authenticated:
                quiz = save_ai_quiz(topic, ai_data, request.user)
                quiz_id = quiz.id

            return Response({
                "success": True,
                "quiz_id": quiz_id,  # Dla gościa będzie to po prostu null
                "questions": ai_data
            })

        except Exception as e:
            print("\n error: \n")
            print(traceback.format_exc())

            return Response({
                "success": False,
                "error": str(e)
            }, status=500)