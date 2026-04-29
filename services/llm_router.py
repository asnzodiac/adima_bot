import os
import requests
import itertools

# Load keys
GROQ_KEYS = [
    os.getenv("GROQ_API_KEY"),
    os.getenv("GROQ_API_KEY1"),
    os.getenv("GROQ_API_KEY2"),
    os.getenv("GROQ_API_KEY3"),
    os.getenv("GROQ_API_KEY4"),
]

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Remove None keys
GROQ_KEYS = [k for k in GROQ_KEYS if k]

key_cycle = itertools.cycle(GROQ_KEYS)

def load_character():
    try:
        with open("character.txt", "r", encoding="utf-8") as f:
            return f.read()
    except:
        return "You are a helpful assistant."

def ask_groq(message):
    system_prompt = load_character()

    for _ in range(len(GROQ_KEYS)):
        key = next(key_cycle)

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": message},
            ],
        }

        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
        except Exception:
            continue

    raise Exception("All GROQ keys failed.")

def ask_openrouter(message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "user", "content": message}
        ],
    }

    r = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )

    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def ask_llm(message):
    try:
        return ask_groq(message)
    except:
        return ask_openrouter(message)
