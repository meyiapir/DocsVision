import requests
import json


class LLM:
    def __init__(self, url: str, model: str) -> None:
        self.model = model
        self.url = url

    def create(self, messages: list[dict[str, str]], to_dict=False) -> str:
        data = {
            "messages": messages,
            "model": self.model
        }
        r = requests.post(f"{self.url}/v1/chat/completions", json=data)

        response = json.loads(r.content.decode("utf-8"))

        if to_dict:
            return response
        else:
            return response["choices"][0]["message"]["content"]


llm = LLM(url="",
           model="TheBloke/Mistral-7B-Instruct-v0.1-AWQ")

messages=[
    {"role": "system", "content": "Ты ассистент-помощник."},
    {"role": "user", "content": "Расскажи мне шутку."},
]

print(llm.create(messages))
