import requests
import json
import re
from django.conf import settings
from .models import Quiz, Question, Answer

def get_ai_quiz(topic, question_count=5, difficulty="easy"):
    api_key = settings.GOOGLE_API_KEY
    model = "gemini-1.5-pro" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    
    headers = {
        "Content-Type": "application/json"
    }
    
    prompt = f"""Create quiz about: {topic} with {difficulty} difficulty and exactly {question_count} questions.
    Answer only in the following json format: [{{"q": "pytanie", "a": ["odp1", "odp2", "odp3", "odp4"], "correct": "odp1"}}] and nothing else"""

    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code == 200:
            full_data = response.json()
            
            try:
                content = full_data['candidates'][0]['content']['parts'][0]['text']
                
                content = re.sub(r"```json", "", content)
                content = re.sub(r"```", "", content)
                content = content.strip()
                
                return json.loads(content)
            except (KeyError, IndexError):
                return {"error": "Nieoczekiwany format odpowiedzi Gemini", "raw": full_data}
            except json.JSONDecodeError:
                return {"error": "AI wypluło niepoprawny JSON", "raw": content}
        
        return {"error": f"Błąd Google API: {response.status_code}", "details": response.text}

    except requests.exceptions.RequestException as e:
        return {"error": "Błąd połączenia", "details": str(e)}

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