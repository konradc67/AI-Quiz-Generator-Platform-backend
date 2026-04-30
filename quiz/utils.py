import requests
import json
from django.conf import settings
from .models import Quiz, Question, Answer
import re

def get_ai_quiz(topic, question_count=10, difficulty="medium"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""Create quiz about: {topic}. 
Difficulty level: {difficulty}. 
Number of questions: {question_count}.
Always answer in the following json format: [{{"q": "pytanie", "a": ["odp1", "odp2", "odp3", "odp4"], "correct": "odp1"}}] 
Only json is allowed as an answer. No explanation or other text is allowed."""

    payload = {
        "model": "openai/gpt-oss-20b:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        full_data = response.json()
        content = full_data['choices'][0]['message']['content']
        
        try:
            content = re.sub(r"```json", "", content)
            content = re.sub(r"```", "", content)
            content = content.strip()
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "AI wypluło śmieci zamiast JSONa", "raw": content}
            
    return {"error": "Błąd połączenia z OpenRouter", "details": response.text}

def save_ai_quiz(topic, ai_data, user=None):
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
                correct=(ans == item["correct"]),
                question=question
            )

    return quiz