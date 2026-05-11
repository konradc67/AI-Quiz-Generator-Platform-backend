import requests
import json
from django.conf import settings
from .models import Quiz, Question, Answer

# USUNIĘTO: from . import views (to powodowało błąd kołowego importu)

def get_ai_quiz(topic, question_count=10, difficulty="medium"):
    api_key = settings.GOOGLE_API_KEY
    model = "gemini-2.5-flash" 
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # POPRAWKA: Używamy czystych zmiennych przekazanych z funkcji (topic i difficulty)
    prompt = f"""Twoim ZADANIEM jest stworzenie quizu wyłącznie na temat: "{topic}".
    Poziom trudności: {difficulty}. 
    Liczba pytań: dokładnie {question_count}.
    WAŻNE ZASADY:
    1. Pytania i odpowiedzi MUSZĄ być w języku takim jak ten, w którym jest podany temat.
    2. Pytania MUSZĄ ściśle dotyczyć podanego tematu ("{topic}"). 
    3. NIE WOLNO Ci generować ogólnych pytań z wiedzy powszechnej (takich jak stolica Francji czy czerwona planeta), chyba że podany temat dokładnie tego dotyczy."""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        # Obniżamy filtry bezpieczeństwa, żeby AI nie blokowało trudnych/historycznych tematów
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "ARRAY",
                "items": {
                    "type": "OBJECT",
                    "properties": {
                        "q": {"type": "STRING", "description": "Treść pytania"},
                        "a": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                            "description": "Lista 4 możliwych odpowiedzi"
                        },
                        "correct": {"type": "STRING", "description": "Dokładna treść poprawnej odpowiedzi (musi być jedną z wartości z listy 'a')"}
                    },
                    "required": ["q", "a", "correct"]
                }
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()

        if response.status_code == 200:
            try:
                content = res_json['candidates'][0]['content']['parts'][0]['text']
                return json.loads(content)
            except (KeyError, IndexError, json.JSONDecodeError) as e:
                return {"error": "Błąd parsowania odpowiedzi AI", "details": str(e), "raw": res_json}
        
        return {"error": f"Błąd Google API: {response.status_code}", "details": res_json}

    except Exception as e:
        return {"error": "Błąd krytyczny połączenia", "details": str(e)}

def save_ai_quiz(topic, ai_data, user=None):
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
                correct=(ans.strip() == item["correct"].strip()),
                question=question
            )

    return quiz