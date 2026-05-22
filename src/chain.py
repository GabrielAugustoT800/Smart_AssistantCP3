import json
from src.llm_client import LLMClient
from src.schemas import ClassificacaoSchema, ProcessamentoSchema, RespostaSchema
from src.prompts import (
    PROMPT_CLASSIFICAR,
    PROMPT_PROCESSAR_EMERGENCIA,
    PROMPT_PROCESSAR_CONSULTA,
    PROMPT_PROCESSAR_INFORMACAO,
    PROMPT_PROCESSAR_MEDICAMENTO,
    PROMPT_RESPONDER
)
from pydantic import ValidationError

class AssistantChain:
    def __init__(self, system_prompt: str):
        self.llm = LLMClient()
        self.system_prompt = system_prompt

    def _parse_json(self, texto: str) -> dict:
        try:
            # Remove possíveis markdown code blocks
            texto = texto.strip()
            if texto.startswith("```"):
                texto = texto.split("```")[1]
                if texto.startswith("json"):
                    texto = texto[4:]
            return json.loads(texto.strip())
        except json.JSONDecodeError as e:
            print(f"Erro ao parsear JSON: {e}")
            return {}
    
    def etapa1_classificar(self, texto_usuario: str) -> ClassificacaoSchema | None:
        prompt = PROMPT_CLASSIFICAR.format(texto=texto_usuario)
        resultado = self.llm.chat(prompt=prompt, system=self.system_prompt)

        if 'erro' in resultado:
            print(f"Erro na etapa 1: {resultado['erro']}")
            return None

        dados = self._parse_json(resultado['resposta'])

        try:
            return ClassificacaoSchema(**dados)
        except ValidationError as e:
            print(f"Validação falhou na etapa 1: {e}")
            return None

    def etapa2_processar(self, classificacao: ClassificacaoSchema, texto_usuario: str) -> ProcessamentoSchema | None:
        prompts_por_tipo = {
            'emergencia': PROMPT_PROCESSAR_EMERGENCIA,
            'consulta': PROMPT_PROCESSAR_CONSULTA,
            'informacao': PROMPT_PROCESSAR_INFORMACAO,
            'medicamento': PROMPT_PROCESSAR_MEDICAMENTO,
        }

        template = prompts_por_tipo.get(classificacao.tipo)
        if not template:
            print(f"Tipo desconhecido: {classificacao.tipo}")
            return None

        prompt = template.format(
            texto=texto_usuario,
            tema=classificacao.tema,
            urgencia=classificacao.urgencia
        )

        resultado = self.llm.chat(prompt=prompt, system=self.system_prompt)

        if 'erro' in resultado:
            print(f"Erro na etapa 2: {resultado['erro']}")
            return None

        dados = self._parse_json(resultado['resposta'])

        try:
            return ProcessamentoSchema(**dados)
        except ValidationError as e:
            print(f"Validação falhou na etapa 2: {e}")
            return None

    def etapa3_responder(self, processamento: ProcessamentoSchema, classificacao: ClassificacaoSchema) -> RespostaSchema | None:
        prompt = PROMPT_RESPONDER.format(
            analise=processamento.analise,
            dados=json.dumps(processamento.dados_extraidos, ensure_ascii=False),
            tipo=classificacao.tipo,
            urgencia=classificacao.urgencia
        )

        resultado = self.llm.chat(prompt=prompt, system=self.system_prompt)

        if 'erro' in resultado:
            print(f"Erro na etapa 3: {resultado['erro']}")
            return None

        dados = self._parse_json(resultado['resposta'])

        try:
            return RespostaSchema(**dados)
        except ValidationError as e:
            print(f"Validação falhou na etapa 3: {e}")
            return None

    def executar(self, texto_usuario: str) -> RespostaSchema | None:
        print("\n🔗 Iniciando pipeline...")

        print("Etapa 1: Classificando...")
        classificacao = self.etapa1_classificar(texto_usuario)
        if not classificacao:
            return None

        print(f"✅ Tipo: {classificacao.tipo} | Urgência: {classificacao.urgencia}")

        # Etapa condicional - escolhe o prompt certo conforme o tipo da etapa 1
        print("Etapa 2: Processando...")
        processamento = self.etapa2_processar(classificacao, texto_usuario)
        if not processamento:
            return None

        print("Etapa 3: Gerando resposta...")
        resposta = self.etapa3_responder(processamento, classificacao)
        if not resposta:
            return None

        print("✅ Pipeline concluído.")
        return resposta

