import requests


class LMStudioClient:
    def __init__(
        self,
        url="http://localhost:1234/v1/chat/completions",
        model="mistral-7b-instruct",
    ):
        self.url = url
        self.model = model

    def ask(self, prompt, max_tokens=64, temperature=0.2):
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        response = requests.post(self.url, json=payload)
        response.raise_for_status()
        return response.json()["choices"][0]["message"]["content"]
