import re
from src.llm_client import LLMClient

class GuardrailSystem:
    def __init__(self):
        self.max_chars = 500
        self.caracteres_proibidos = ['<', '>', '{', '}']
        self.padroes_injection = [
            r'ignore\s+(all\s+)?(previous|prior|above)\s+instructions?',
            r'forget\s+(all\s+)?(previous|prior|above|your)\s+(instructions?|rules?|context)',
            r'you\s+are\s+now\s+',
            r'jailbreak',
            r'\bDAN\b',
            r'act\s+as\s+(if\s+you\s+are|a)',
            r'reveal\s+(your\s+)?(system\s+)?prompt',
            r'ignore\s+(your\s+)?(rules?|guidelines?|restrictions?)',
            r'pretend\s+(you\s+are|to\s+be)',
            r'disable\s+(your\s+)?(safety|filters?|restrictions?)',
        ]

    
    # INPUT GUARD
    # cobre tamanho, caracteres proibidos e 10 padrões de injection
    def validar_input(self, texto: str) -> tuple[bool, str]:
        if not texto or not texto.strip():
            return False, "Entrada vazia."

        if len(texto) > self.max_chars:
            return False, f"Entrada muito longa. Máximo: {self.max_chars} caracteres."

        for char in self.caracteres_proibidos:
            if char in texto:
                return False, f"Caractere proibido detectado: '{char}'"

        texto_lower = texto.lower()
        for padrao in self.padroes_injection:
            if re.search(padrao, texto_lower):
                return False, "Tentativa de prompt injection detectada."

        return True, "OK"

    
    # OUTPUT GUARD
    # verifica se houve vazamento do system prompt e respostas fora do domínio
    def validar_output(self, resposta: str, system_prompt: str) -> tuple[bool, str]:
        if not resposta or not resposta.strip():
            return False, "Resposta vazia."

        # Verifica se vazou conteúdo do system prompt
        trechos_sensiveis = [
            linha.strip()
            for linha in system_prompt.splitlines()
            if len(linha.strip()) > 30
        ]
        for trecho in trechos_sensiveis:
            if trecho.lower() in resposta.lower():
                return False, "Resposta contém conteúdo do system prompt."

        # Verifica se está fora do domínio
        termos_fora_dominio = [
            'receita de bolo', 'futebol', 'política', 'programação',
            'investimento', 'viagem', 'música'
        ]
        resposta_lower = resposta.lower()
        for termo in termos_fora_dominio:
            if termo in resposta_lower:
                return False, f"Resposta fora do domínio de saúde: '{termo}'"

        return True, "OK"