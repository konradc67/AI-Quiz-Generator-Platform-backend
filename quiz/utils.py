import requests
import json
from django.conf import settings

def get_ai_quiz(topic):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    prompt = f"Stwórz quiz o: {topic}. Zwróć tylko JSON: [{{'q': 'pytanie', 'a': ['odp1', 'odp2'], 'correct': 'odp1'}}]"

    payload = {
        "model": "openai/gpt-oss-120b:free",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    
    if response.status_code == 200:
        full_data = response.json()
        content = full_data['choices'][0]['message']['content']
        
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"error": "AI wypluło śmieci zamiast JSONa", "raw": content}
            
    return {"error": "Błąd połączenia z OpenRouter", "details": response.text}