import requests
import json
import re
from django.conf import settings
from .models import Quiz, Question, Answer

def get_ai_quiz(topic, question_count=10, difficulty="medium"):
    api_key = settings.GOOGLE_API_KEY
    model = "gemini-2.5-flash" 
    
    # POPRAWKA 1: Zmiana ścieżki z /v1/ na /v1beta/
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Skrócony prompt – nie musimy już "błagać" modelu o brak markdownu
    prompt = f"""Create a quiz about: {topic} with {difficulty} difficulty and exactly {question_count} questions.
    Return the response ONLY as a JSON array of objects. 
    Format: [{{"q": "pytanie", "a": ["odp1", "odp2", "odp3", "odp4"], "correct": "odp1"}}]"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        # POPRAWKA 2: Wymuszenie czystego JSON-a natywną metodą API
        # Zwróć uwagę na camelCase: responseMimeType (to rozwiązuje Twój wcześniejszy błąd 400)
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()

        if response.status_code == 200:
            try:
                # W Gemini tekst znajduje się w candidates -> content -> parts -> text
                content = res_json['candidates'][0]['content']['parts'][0]['text']
                
                # Model gwarantuje teraz zwrot czystego JSON-a, bez formatowania ```json
                return json.loads(content)
            
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                return {"error": "Błąd parsowania odpowiedzi AI", "details": str(e), "raw": res_json}
        
        return {"error": f"Błąd Google API: {response.status_code}", "details": res_json}

    except Exception as e:
        return {"error": "Błąd krytyczny połączenia", "details": str(e)}

def save_ai_quiz(topic, ai_data, user=None):
    # Jeśli ai_data to słownik z błędem, przerywamy
    if isinstance(ai_data, dict) and "error" in ai_data:
        print(f"Nie można zapisać quizu: {ai_data['error']}")
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
                # Czyścimy spacje, żeby porównanie było pewne
                correct=(ans.strip() == item["correct"].strip()),
                question=question
            )

    return quiz