import json
import tiktoken
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path


# CONTAGEM DE TOKENS
def contar_tokens(texto: str, modelo: str = 'gpt-4') -> int:
    try:
        enc = tiktoken.encoding_for_model(modelo)
        return len(enc.encode(texto))
    except Exception:
        return len(texto.split())


# CARREGAMENTO DE DATASETS
def carregar_datasets(caminho: str) -> list:
    with open(caminho, 'r', encoding='utf-8') as f:
        return json.load(f)


# CARREGAMENTO DE PROMPT POR VERSÃO
def carregar_prompt_versao(versao: str) -> str:
    caminho = Path(f'prompts/versions/{versao}.txt')
    with open(caminho, 'r', encoding='utf-8') as f:
        return f.read()


# AVALIAÇÃO PRINCIPAL
def avaliar(chain, guardrails, system_prompt: str):
    chain.system_prompt = system_prompt
    resultados = []

    test_dataset = carregar_datasets('data/test_dataset.json')
    attack_dataset = carregar_datasets('data/attack_dataset.json')

    # Testes legítimos
    print("\n --- Rodando Testes Legítimos... ---")
    for caso in test_dataset:
        texto = caso['texto']
        tipo_esperado = caso['tipo_esperado']
        urgencia_esperada = caso['urgencia_esperada']
        palavras_chave = caso.get('palavras_chave', [])

        is_safe, motivo = guardrails.validar_input(texto)

        if not is_safe:
            resultados.append({
                'texto': texto,
                'tipo': 'legitimo',
                'bloqueado': True,
                'falso_positivo': True,
                'tipo_correto': False,
                'urgencia_correta': False,
                'json_valido': False,
                'palavras_chave_ok': False,
                'motivo': motivo
            })
            continue

        resposta = chain.executar(texto)
        json_valido = resposta is not None

        tipo_correto = False
        urgencia_correta = False
        palavras_chave_ok = False

        if json_valido:
            classificacao = chain.etapa1_classificar(texto)
            tipo_correto = classificacao is not None and classificacao.tipo == tipo_esperado
            urgencia_correta = classificacao is not None and classificacao.urgencia == urgencia_esperada
            palavras_chave_ok = all(
                palavra.lower() in resposta.resposta.lower()
                for palavra in palavras_chave
            ) if palavras_chave else True

        resultados.append({
            'texto': texto,
            'tipo': 'legitimo',
            'bloqueado': False,
            'falso_positivo': False,
            'tipo_correto': tipo_correto,
            'urgencia_correta': urgencia_correta,
            'json_valido': json_valido,
            'palavras_chave_ok': palavras_chave_ok,
            'motivo': ''
        })

    # Testes de ataque
    print(" --- Rodando testes de ataque... ---")
    for ataque in attack_dataset:
        texto = ataque['texto']

        is_safe, motivo = guardrails.validar_input(texto)
        bloqueado = not is_safe

        resultados.append({
            'texto': texto,
            'tipo': 'ataque',
            'bloqueado': bloqueado,
            'falso_positivo': False,
            'tipo_correto': False,
            'urgencia_correta': False,
            'json_valido': False,
            'palavras_chave_ok': False,
            'motivo': motivo
        })

    return resultados


# AVALIAÇÃO POR VERSÃO DE PROMPT
def avaliar_versoes(chain, guardrails):
    versoes = ['v1', 'v2', 'v3']
    metricas_por_versao = {}

    print("\n --- Comparando versões de prompt... ---")
    for versao in versoes:
        print(f"\n🔄 Avaliando {versao}...")
        system_prompt = carregar_prompt_versao(versao)
        chain.system_prompt = system_prompt
        resultados = avaliar(chain, guardrails, system_prompt)
        metricas_por_versao[versao] = calcular_metricas(resultados, chain)

    return metricas_por_versao


# MÉTRICAS
def calcular_metricas(resultados: list, chain) -> dict:
    legitimos = [r for r in resultados if r['tipo'] == 'legitimo']
    ataques = [r for r in resultados if r['tipo'] == 'ataque']

    acuracia_classificacao = (
        sum(1 for r in legitimos if r['tipo_correto']) / len(legitimos)
        if legitimos else 0
    )

    acuracia_urgencia = (
        sum(1 for r in legitimos if r['urgencia_correta']) / len(legitimos)
        if legitimos else 0
    )

    taxa_json_valido = (
        sum(1 for r in legitimos if r['json_valido']) / len(legitimos)
        if legitimos else 0
    )

    taxa_bloqueio = (
        sum(1 for r in ataques if r['bloqueado']) / len(ataques)
        if ataques else 0
    )

    taxa_falso_positivo = (
        sum(1 for r in legitimos if r['falso_positivo']) / len(legitimos)
        if legitimos else 0
    )

    taxa_consistencia = calcular_consistencia(chain)

    return {
        'acuracia_classificacao': round(acuracia_classificacao * 100, 2),
        'acuracia_urgencia': round(acuracia_urgencia * 100, 2),
        'taxa_json_valido': round(taxa_json_valido * 100, 2),
        'taxa_bloqueio': round(taxa_bloqueio * 100, 2),
        'taxa_falso_positivo': round(taxa_falso_positivo * 100, 2),
        'taxa_consistencia': taxa_consistencia
    }


def calcular_consistencia(chain) -> float:
    # Roda a mesma solicitação 3x e verifica se o tipo é igual nas 3
    texto_teste = "Estou com febre de 38 graus há dois dias"
    tipos = []

    for _ in range(3):
        classificacao = chain.etapa1_classificar(texto_teste)
        if classificacao:
            tipos.append(classificacao.tipo)

    if len(tipos) < 3:
        return 0.0

    # Consistente se os 3 resultados forem iguais
    consistente = len(set(tipos)) == 1
    return 100.0 if consistente else 0.0


# RELATÓRIO
def gerar_relatorio(resultados: list, metricas: dict, metricas_por_versao: dict = None):
    Path('output').mkdir(exist_ok=True)
    Path('output/graficos').mkdir(exist_ok=True)

    # CSV
    df = pd.DataFrame(resultados)
    df.to_csv('output/eval_resultados.csv', index=False, encoding='utf-8')
    print("\n - Relatório salvo em output/eval_resultados.csv")

    # Gráfico 1 — Métricas gerais
    labels = [
        'Acurácia\nClassificação',
        'Acurácia\nUrgência',
        'JSON\nVálido',
        'Taxa de\nBloqueio',
        'Falso\nPositivo',
        'Consistência'
    ]
    valores = [
        metricas['acuracia_classificacao'],
        metricas['acuracia_urgencia'],
        metricas['taxa_json_valido'],
        metricas['taxa_bloqueio'],
        metricas['taxa_falso_positivo'],
        metricas['taxa_consistencia']
    ]

    plt.figure(figsize=(10, 5))
    bars = plt.bar(labels, valores, color=['#4CAF50', '#8BC34A', '#2196F3', '#FF5722', '#FF9800', '#9C27B0'])
    plt.title('Métricas de Avaliação — MedTriage Bot')
    plt.ylabel('Percentual (%)')
    plt.ylim(0, 110)
    for bar, val in zip(bars, valores):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f'{val}%', ha='center')
    plt.tight_layout()
    plt.savefig('output/graficos/metricas_gerais.png')
    plt.close()
    print("📊 Gráfico salvo em output/graficos/metricas_gerais.png")

    # Gráfico 2 — Distribuição legítimos vs ataques
    tipos = df['tipo'].value_counts()
    plt.figure(figsize=(6, 6))
    plt.pie(tipos.values, labels=tipos.index, autopct='%1.1f%%', colors=['#2196F3', '#FF5722'])
    plt.title('Distribuição: Legítimos vs Ataques')
    plt.tight_layout()
    plt.savefig('output/graficos/distribuicao_casos.png')
    plt.close()
    print("📊 Gráfico salvo em output/graficos/distribuicao_casos.png")

    # Gráfico 3 — Comparação entre versões de prompt
    if metricas_por_versao:
        versoes = list(metricas_por_versao.keys())
        metricas_labels = [
            'acuracia_classificacao',
            'acuracia_urgencia',
            'taxa_json_valido',
            'taxa_bloqueio'
        ]
        cores = ['#4CAF50', '#8BC34A', '#2196F3', '#FF5722']

        x = range(len(versoes))
        largura = 0.2

        plt.figure(figsize=(12, 6))
        for i, (metrica, cor) in enumerate(zip(metricas_labels, cores)):
            valores_versao = [metricas_por_versao[v][metrica] for v in versoes]
            offset = [xi + i * largura for xi in x]
            bars = plt.bar(offset, valores_versao, width=largura, label=metrica.replace('_', ' ').title(), color=cor)
            for bar, val in zip(bars, valores_versao):
                plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f'{val}%', ha='center', fontsize=8)

        plt.title('Evolução das Métricas por Versão de Prompt')
        plt.ylabel('Percentual (%)')
        plt.ylim(0, 120)
        plt.xticks([xi + largura * 1.5 for xi in x], versoes)
        plt.legend(loc='upper left')
        plt.tight_layout()
        plt.savefig('output/graficos/evolucao_versoes.png')
        plt.close()
        print("📊 Gráfico salvo em output/graficos/evolucao_versoes.png")

    # Resumo no terminal
    print("\n📈 MÉTRICAS FINAIS:")
    for k, v in metricas.items():
        print(f"  {k}: {v}%")