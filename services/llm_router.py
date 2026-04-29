import os
import requests
import itertools

# ==========================
# LOAD API KEYS
# ==========================

GROQ_KEYS = [
    os.getenv("GROQ_API_KEY"),
    os.getenv("GROQ_API_KEY1"),
    os.getenv("GROQ_API_KEY2"),
    os.getenv("GROQ_API_KEY3"),
    os.getenv("GROQ_API_KEY4"),
]

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Remove empty keys
GROQ_KEYS = [k for k in GROQ_KEYS if k]

if GROQ_KEYS:
    key_cycle = itertools.cycle(GROQ_KEYS)
else:
    key_cycle = None


# ==========================
# CHARACTER PROMPT
# ==========================

def load_character():
    try:
        with open("character.txt", "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print("⚠ character.txt load failed:", e)
        return "You are a helpful assistant."


# ==========================
# GROQ CALL
# ==========================

def ask_groq(message):
    if not GROQ_KEYS:
        raise Exception("No GROQ keys configured.")

    system_prompt = load_character()

    for _ in range(len(GROQ_KEYS)):
        key = next(key_cycle)

        headers = {
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.3-70b-versatile",
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
                timeout=20,  # ✅ reduced timeout
            )

            r.raise_for_status()

            data = r.json()

            if "choices" in data and data["choices"]:
                return data["choices"][0]["message"]["content"]

            print("⚠ Unexpected GROQ response:", data)

        except Exception as e:
            print("⚠ GROQ key failed:", e)
            continue

    raise Exception("All GROQ keys failed.")


# ==========================
# OPENROUTER FALLBACK
# ==========================

def ask_openrouter(message):
    if not OPENROUTER_API_KEY:
        raise Exception("No OpenRouter key configured.")

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

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=20,
        )

        r.raise_for_status()

        data = r.json()

        if "choices" in data and data["choices"]:
            return data["choices"][0]["message"]["content"]

        print("⚠ Unexpected OpenRouter response:", data)

    except Exception as e:
        print("⚠ OpenRouter failed:", e)

    return "⚠ AI service is temporarily unavailable."


# ==========================
# MAIN ROUTER
# ==========================

def ask_llm(message):
    try:
        return ask_groq(message)
    except Exception as e:
        print("⚠ GROQ failed, switching to OpenRouter:", e)
        return ask_openrouter(message)
