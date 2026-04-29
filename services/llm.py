import os
import requests

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def load_character():
    try:
        with open("character.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "You are a helpful assistant."

def ask_llm(user_message: str):
    system_prompt = load_character()

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    }

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]
