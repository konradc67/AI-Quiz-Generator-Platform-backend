from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from .models import Quiz
from .utils import get_ai_quiz, save_ai_quiz
import traceback
import json  # WAŻNE: Dodano import json do awaryjnego parsowania!

def home(request):
    return render(request, 'quiz/home.html')

class QuizGenerateView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        try:
            print("\n--- 1. DANE Z FRONTENDU (request.data):", request.data)
            
            # Awaryjne wyciąganie danych, jeśli DRF zgubił request.data
            if not request.data and request.body:
                print("--- 2. Używam awaryjnego parsowania request.body...")
                body_unicode = request.body.decode('utf-8')
                body_data = json.loads(body_unicode)
                topic = body_data.get('prompt') or body_data.get('topic')
                question_count = body_data.get('questionCount', 5)
                difficulty = body_data.get('difficulty', 'easy')
            else:
                topic = request.data.get('prompt') or request.data.get('topic')
                question_count = request.data.get('questionCount', 5)
                difficulty = request.data.get('difficulty', 'easy')
            
            print(f"--- 3. TEMAT DO WYSŁANIA: '{topic}'")

            # KULOODPORNA BLOKADA: Jeśli temat to None, pusty string lub domyślny, przerywamy!
            if not topic or str(topic).strip() == "" or topic == "General Knowledge":
                return Response({
                    "success": False, 
                    "error": "BŁĄD: Backend nie otrzymał tematu z frontendu! Temat jest pusty."
                }, status=400)

            # Wysyłamy do AI
            ai_data = get_ai_quiz(topic, question_count, difficulty)
            
            if isinstance(ai_data, dict) and "error" in ai_data:
                return Response({"success": False, "error": ai_data}, status=400)

            quiz_id = None
            
            if request.user.is_authenticated:
                quiz = save_ai_quiz(topic, ai_data, request.user)
                quiz_id = quiz.id if quiz else None

            return Response({
                "success": True,
                "quiz_id": quiz_id,
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
            quiz = Quiz.objects.get(id=quiz_id, author=request.user)
            questions_data = []
            
            for q in quiz.questions.all():
                answers = []
                correct_answer = ""
                
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
        
class DashboardStatsView(APIView):
    def get(self, request):
        try:
            user_quizzes = Quiz.objects.filter(author=request.user)
            total_quizzes = user_quizzes.count()
            
            total_questions = user_quizzes.aggregate(Sum('questions_count'))['questions_count__sum'] or 0
            
            latest_quiz = user_quizzes.order_by('-id').first()
            last_activity = latest_quiz.created_at if latest_quiz else "No activity yet"

            return Response({
                "success": True,
                "total_quizzes": total_quizzes,
                "total_questions": total_questions,
                "last_activity": last_activity
            }, status=200)

        except Exception as e:
            print(traceback.format_exc())
            return Response({"success": False, "error": str(e)}, status=500)