import os

from openai import OpenAI

print("=== agent_smalltalk.py IMPORTED ===")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM = (
    "Tu es SENTRA CORE, assistant IA cordial. "
    "Réponds en français, 3 phrases maximum."
)


def run(user_message: str) -> dict:
    """Renvoie une réponse courte en français via GPT‑3.5‑turbo."""
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": user_message},
            ],
            temperature=0.7,
            max_tokens=120,
        )
        answer = resp.choices[0].message.content.strip()
    except Exception as exc:
        answer = f"(Erreur OpenAI v1 : {exc})"

    return {
        "réponse": answer,
        "glyph": "💬",
    }
