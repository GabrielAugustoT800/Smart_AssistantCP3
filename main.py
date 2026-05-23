import sys
from pathlib import Path
from dotenv import load_dotenv
from src.chain import AssistantChain
from src.guardrails import GuardrailSystem
from src.evaluator import avaliar, calcular_metricas, gerar_relatorio, avaliar_versoes

load_dotenv()

BASE_DIR = Path(__file__).parent

def carregar_system_prompt() -> str:
    with open(BASE_DIR/'prompts'/'system_prompt.txt', 'r', encoding= 'utf-8') as f:
        return f.read()
    
def modo_interativo(chain: AssistantChain, guardrails: GuardrailSystem):
    print("\n🏥 MedTriage Bot - Assistente de Saúde")
    print("Digite 'sair' para encerrar.\n")

    while True:
        texto = input("Você: ").strip()

        if texto.lower() == 'sair':
            print("\nEncerrando MedTriage Bot. Cuide-se! 👋")
            break

        # Input Guard
        is_safe, motivo = guardrails.validar_input(texto)
        if not is_safe:
            print(f"⛔ Entrada bloqueada: {motivo}\n")

        # Pipeline
        resposta = chain.executar(texto)
        if not resposta:
            print("Não foi possível acessar sua solicitação. Tente novamente.\n")
            continue

        # Output Guard
        system_prompt = carregar_system_prompt()
        is_safe, motivo = guardrails.validar_output(resposta.resposta, system_prompt)
        if not is_safe:
            print(f"⛔ Resposta bloqueada: {motivo}\n")
            continue

        # Exibe a resposta
        print(f"\n🤖 Dr. Ivan: {resposta.resposta}")
        print(f"💡 Ação sugerida: {resposta.acao_sugerida}")
        if resposta.disclaimer:
            print(f"  {resposta.disclaimer}")
            print(f" Confiança: {resposta.confianca}\n")

def modo_avaliacao(chain: AssistantChain, guardrails: GuardrailSystem, system_prompt: str):
    print("\n📊 Iniciando modo de avaliação...")
    resultados = avaliar(chain, guardrails, system_prompt)
    metricas = calcular_metricas(resultados, chain)
    metricas_por_versao = avaliar_versoes(chain, guardrails)
    gerar_relatorio(resultados, metricas, metricas_por_versao)
    print("\n✅ Avaliação concluída.")

def main():
    system_prompt = carregar_system_prompt()
    chain = AssistantChain(system_prompt=system_prompt)
    guardrails = GuardrailSystem()

    if len(sys.argv) > 1 and sys.argv[1] == '--avaliar':
        modo_avaliacao(chain, guardrails, system_prompt)
    else:
        modo_interativo(chain, guardrails)

if __name__ == '__main__':
    main()