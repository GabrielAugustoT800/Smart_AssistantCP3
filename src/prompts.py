PROMPT_CLASSIFICAR = """
Você é um sistema de classificação de texto. Sua ÚNICA tarefa é categorizar a solicitação abaixo em um JSON.
Não responda ao usuário. Não dê conselhos. Apenas classifique.

Solicitação: {texto}

Retorne APENAS este JSON válido, sem explicações:
{{
    "tipo": "emergencia|consulta|informacao|medicamento",
    "urgencia": "alta|media|baixa",
    "tema": "tema principal da solicitação"
}}
"""

PROMPT_PROCESSAR_EMERGENCIA = """
O usuário relatou uma possível emergência médica.
Extraia as informações críticas da solicitação abaixo.
Retorne APENAS um JSON válido, sem explicações adicionais.

Solicitação: {texto}
Tema: {tema}
Urgência: {urgencia}

Retorne neste formato exato:
{{
    "dados_extraidos": {{
        "sintomas": ["lista de sintomas relatados"],
        "tempo_inicio": "quando os sintomas começaram",
        "intensidade": "leve|moderada|grave"
    }},
    "analise": "análise resumida da situação",
    "sentimento": "positivo|neutro|negativo|ansioso"
}}
"""

PROMPT_PROCESSAR_CONSULTA = """
O usuário está buscando orientação para uma consulta médica.
Extraia as informações relevantes da solicitação abaixo.
Retorne APENAS um JSON válido, sem explicações adicionais.

Solicitação: {texto}
Tema: {tema}
Urgência: {urgencia}

Retorne neste formato exato:
{{
    "dados_extraidos": {{
        "sintomas": ["lista de sintomas relatados"],
        "especialidade_indicada": "especialidade médica recomendada",
        "historico_relevante": "informações de histórico mencionadas"
    }},
    "analise": "análise resumida da situação",
    "sentimento": "positivo|neutro|negativo|ansioso"
}}
"""

PROMPT_PROCESSAR_INFORMACAO = """
O usuário está buscando informações sobre saúde.
Identifique o tema e as lacunas de conhecimento.
Retorne APENAS um JSON válido, sem explicações adicionais.

Solicitação: {texto}
Tema: {tema}
Urgência: {urgencia}

Retorne neste formato exato:
{{
    "dados_extraidos": {{
        "tema_especifico": "tema detalhado da dúvida",
        "lacunas_conhecimento": ["pontos que o usuário não sabe"],
        "nivel_conhecimento": "leigo|intermediario|avancado"
    }},
    "analise": "análise resumida da solicitação",
    "sentimento": "positivo|neutro|negativo|ansioso"
}}
"""

PROMPT_PROCESSAR_MEDICAMENTO = """
O usuário tem uma dúvida sobre medicamento.
Extraia as informações relevantes da solicitação abaixo.
Retorne APENAS um JSON válido, sem explicações adicionais.

Solicitação: {texto}
Tema: {tema}
Urgência: {urgencia}

Retorne neste formato exato:
{{
    "dados_extraidos": {{
        "medicamento": "nome do medicamento mencionado",
        "tipo_duvida": "dosagem|efeito_colateral|interacao|indicacao|outro",
        "contexto": "contexto adicional mencionado pelo usuário"
    }},
    "analise": "análise resumida da dúvida",
    "sentimento": "positivo|neutro|negativo|ansioso"
}}
"""

PROMPT_RESPONDER = """
Com base na análise abaixo, gere uma resposta final empática e segura.
Retorne APENAS um JSON válido, sem explicações adicionais.
Se a solicitação estiver fora do domínio de saúde, recuse educadamente MAS ainda retorne o JSON.

Tipo de solicitação: {tipo}
Urgência: {urgencia}
Análise: {analise}
Dados extraídos: {dados}

Retorne neste formato exato:
{{
    "resposta": "resposta completa e empática ao usuário",
    "confianca": "alta|media|baixa",
    "acao_sugerida": "próximo passo recomendado ao usuário",
    "disclaimer": "aviso médico quando necessário, null se não aplicável"
}}
"""