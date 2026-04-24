from django.shortcuts import render
from django.http import HttpResponse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .utils import get_ai_quiz, save_ai_quiz
import traceback

def home(request):
    return render(request, 'quiz/home.html')

class QuizGenerateView(APIView):
    permission_classes=[AllowAny]
    def post(self, request):
        try:
            topic = request.data.get('topic', 'General Knowledge')
            user = request.user if request.user.is_authenticated else None
            ai_data = get_ai_quiz(topic)
            if isinstance(ai_data, dict) and "error" in ai_data:
                return Response({"success": False, "error": ai_data}, status=400)

            quiz = save_ai_quiz(topic, ai_data, user)

            return Response({
                "success": True,
                "quiz_id": quiz.id,
                "questions": ai_data})

        except Exception as e:
            print("\n error: \n")
            print(traceback.format_exc())

            return Response({
                "success": False,
                "error": str(e)
            }, status=500)