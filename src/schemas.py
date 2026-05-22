from pydantic import BaseModel, Field
from typing import Optional

# Etapa 1 - Classificação
class ClassificacaoSchema(BaseModel):
    tipo: str = Field(description="emergencia|consulta|informacao|medicamento")
    urgencia: str = Field(description="alta|media|baixa")
    tema: str = Field(description="Tema principal da solicitação")

# Etapa 2 - Processamento
class ProcessamentoSchema(BaseModel):
    dados_extraidos: dict = Field(description="Dados relevantes extraídos conforme o tipo")
    analise: str = Field(description="Análise detalhada da solicitação")
    sentimento: Optional[str] = Field(default=None, description="positivo|neutro|negativo|ansioso")

# Etapa 3 - Resposta
class RespostaSchema(BaseModel):
    resposta: str = Field(description="Resposta final formatada ao usuário")
    confianca: str = Field(description="alta|media|baixa")
    acao_sugerida: str = Field(description="Próximo passo recomendado ao usuário")
    disclaimer: Optional[str] = Field(default=None, description="Aviso médico quando necessário")