import requests
import json
import re
from django.conf import settings
from .models import Quiz, Question, Answer

def get_ai_quiz(topic, question_count=10, difficulty="medium"):
    api_key = settings.GOOGLE_API_KEY
    # Używamy v1beta, ponieważ najlepiej radzi sobie z modelami 1.5
    model = "gemini-1.5-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    # Przenosimy wymóg JSON-a do promptu, bo pole response_mime_type powodowało u Ciebie błąd 400
    prompt = f"""Create a quiz about: {topic} with {difficulty} difficulty and exactly {question_count} questions.
    Return the response ONLY as a valid JSON array of objects. 
    Format: [{{"q": "pytanie", "a": ["odp1", "odp2", "odp3", "odp4"], "correct": "odp1"}}]
    Do not include any markdown formatting like ```json or any introductory text."""

    # Najprostszy możliwy payload, który nie wywoła błędu "Unknown name"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        res_json = response.json()

        if response.status_code == 200:
            # W Gemini tekst znajduje się w candidates -> content -> parts -> text
            try:
                content = res_json['candidates'][0]['content']['parts'][0]['text']
                
                # Usuwamy ewentualne znaczniki markdown, jeśli model je mimo wszystko dodał
                content = re.sub(r"```json|```", "", content).strip()
                
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