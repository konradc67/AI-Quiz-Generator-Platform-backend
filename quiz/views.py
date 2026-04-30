from django.shortcuts import render
from django.http import HttpResponse

from .models import Quiz

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
        
class QuizHistoryView(APIView):
    def get(self, request):
        try:
            quizzes = Quiz.objects.filter(author=request.user).order_by('-id')
            
            history_data = []
            for q in quizzes:
                history_data.append({
                    "id": q.id,
                    "topic": q.topic,
                    "created_at": q.created_at,
                    "questions_count": q.questions_count
                })

            return Response({
                "success": True,
                "history": history_data
            }, status=200)

        except Exception as e:
            print(traceback.format_exc())
            return Response({"success": False, "error": str(e)}, status=500)

class QuizDetailView(APIView):
    def get(self, request, quiz_id):
        try:
            # 1. Pobieramy quiz upewniając się, że należy do usera
            quiz = Quiz.objects.get(id=quiz_id, author=request.user)
            
            # 2. Wyciągamy pytania i przypisane do nich odpowiedzi
            questions_data = []
            
            # quiz.questions działa, bo w models.py dałeś related_name='questions'
            for q in quiz.questions.all():
                answers = []
                correct_answer = ""
                
                # q.answers działa, bo dałeś related_name='answers'
                for a in q.answers.all():
                    answers.append(a.text)
                    if a.correct:
                        correct_answer = a.text
                        
                questions_data.append({
                    "q": q.text,
                    "a": answers,
                    "correct": correct_answer
                })

            return Response({
                "success": True,
                "topic": quiz.topic,
                "created_at": quiz.created_at,
                "questions": questions_data
            }, status=200)

        except Quiz.DoesNotExist:
            return Response({"success": False, "error": "Quiz nie istnieje lub brak dostępu."}, status=404)
        except Exception as e:
            print(traceback.format_exc())
            return Response({"success": False, "error": str(e)}, status=500)