import requests
import json
import re
from django.conf import settings
from .models import Quiz, Question, Answer

def get_ai_quiz(topic, question_count=10, difficulty="medium"):
    api_key = settings.GOOGLE_API_KEY
    # Używamy wersji v1 i modelu flash dla stabilności
    model = "gemini-1.5-flash" 
    url = f"https://generativelanguage.googleapis.com/v1/models/{model}:generateContent?key={api_key}"
    
    headers = {"Content-Type": "application/json"}
    
    prompt = f"""Create quiz about: {topic} with {difficulty} difficulty and exactly {question_count} questions.
    Answer only in the following json format: [{{"q": "pytanie", "a": ["odp1", "odp2", "odp3", "odp4"], "correct": "odp1"}}] and nothing else"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "responseMimeType": "application/json" 
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()

        if response.status_code == 200:
            # Wyciąganie tekstu z formatu Gemini
            content = res_json['candidates'][0]['content']['parts'][0]['text']
            return json.loads(content)
        else:
            return {"error": f"Błąd API: {response.status_code}", "details": res_json}

    except Exception as e:
        return {"error": "Wyjątek w kodzie", "details": str(e)}

def save_ai_quiz(topic, ai_data, user=None):
    if isinstance(ai_data, dict) and "error" in ai_data:
        return None

    quiz = Quiz.objects.create(
        topic=topic,
        questions_count=len(ai_data),
        author=user
    )

    for item in ai_data:
        question = Question.objects.create(
            text=item["q"],
            answers_count=len(item["a"]),
            quiz=quiz
        )

        for ans in item["a"]:
            Answer.objects.create(
                text=ans,
                correct=(ans.strip() == item["correct"].strip()),
                question=question
            )

    return quiz