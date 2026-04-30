import requests
import json
from django.conf import settings

def get_ai_quiz(topic, question_count, difficulty):
    url = "[https://openrouter.ai/api/v1/chat/completions](https://openrouter.ai/api/v1/chat/completions)"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = (
        f"Stwórz quiz o tematyce: {topic}. "
        f"Poziom trudności: {difficulty}. "
        f"Wygeneruj dokładnie {question_count} pytań. "
        "Zwróć WYŁĄCZNIE surowy JSON bez żadnych bloków formatowania markdown (nie używaj ```json). "
        "Struktura musi wyglądać tak: "
        "[{\"q\": \"pytanie\", \"a\": [\"odp1\", \"odp2\", \"odp3\", \"odp4\"], \"correct\": \"odp1\"}]"
    )

    payload = {
        "model": "google/gemma-4-31b-it:free",  # Model uaktualniony do Gemma
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        full_data = response.json()
        content = full_data['choices'][0]['message']['content']
        
        content = content.replace("```json", "").replace("```", "").strip()
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "AI wypluło śmieci zamiast JSONa", "raw": content}
            
    return {"error": "Błąd połączenia z OpenRouter", "details": response.text}