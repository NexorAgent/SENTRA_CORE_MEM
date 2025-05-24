import openai, os
from dotenv import load_dotenv
from scripts.memory_manager import append_memory, query_memory

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

with open("prompts/sentra_core.prompt.txt", "r", encoding="utf-8") as f:
    prompt_base = f.read()

def build_messages(user_msg):
    memory = "\n".join([e['contenu'] for e in query_memory()])
    return [
        {"role": "system", "content": prompt_base},
        {"role": "system", "content": f"Contexte mémoire :\n{memory}"},
        {"role": "user", "content": user_msg}
    ]

def chat(user_msg):
    messages = build_messages(user_msg)
    res = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=messages,
        temperature=0.3
    )
    answer = res.choices[0].message.content.strip()
    append_memory(answer, typ="réponse")
    return answer

if __name__ == "__main__":
    while True:
        try:
            msg = input("> ")
            print(chat(msg), "\n")
        except KeyboardInterrupt:
            break
