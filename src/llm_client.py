import os
from ollama import Client
from dotenv import load_dotenv
import time
from src.evaluator import contar_tokens

load_dotenv()

client = Client(
    host=os.getenv('OLLAMA_HOST'),
    headers={'Authorization': 'Bearer ' + os.getenv('OLLAMA_API_KEY')}
)

class LLMClient:
    def __init__(self):
        self.model = os.getenv('MODEL_NAME', 'gpt-oss:120b')

    def chat(self, prompt, system='', temp=0.3, max_tokens=500):
        messages = []
        if system:
            messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': prompt})

        try:
            inicio = time.time()
            resultado = client.chat(
                model=self.model,
                messages=messages,
                options={'num_predict': max_tokens, 'temperature': temp},
                stream=False
            )
            resposta = resultado.message.content.strip()
            tempo_ms = int((time.time() - inicio) * 1000)

            return {
                'resposta': resposta,
                'tokens_prompt': contar_tokens(prompt),
                'tokens_resposta': contar_tokens(resposta),
                'tempo_ms': tempo_ms
            }
        except Exception as e:
            print(f'Erro: {e}')
            return {'erro': str(e)}