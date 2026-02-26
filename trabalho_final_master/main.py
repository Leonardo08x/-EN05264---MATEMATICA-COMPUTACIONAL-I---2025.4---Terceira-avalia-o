import time
import tracemalloc
import pandas as pd
from metaheuristica.algoritmo_genetico import algoritmo_genetico
from solver.solve import solver_PLI


def run_comparative_analysis(instancias):
    resultados = []

    for instancia in instancias:
        print(f"\n{'='*60}")
        print(f"PROCESSANDO INSTÂNCIA: {instancia}")

        # --- 1. PREPARAÇÃO (LIGANDO OS SENSORES) ---
        tracemalloc.start()  # Inicia o rastreador de RAM
        start_time = time.time()  # Crava o relógio

        try:
            # --- 2. EXECUÇÃO DA CAIXA PRETA ---
            escala_ga, custo_ga = algoritmo_genetico(instancia)

            # --- 3. LEITURA DOS SENSORES (ANTES DE FAZER QUALQUER OUTRA COISA) ---
            tempo_ga = time.time() - start_time
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()  # Desliga o rastreador

            # Converte bytes para Megabytes (MB)
            memoria_pico_mb = peak_mem / (1024 * 1024)

            escala_ga.to_csv(
                f"resultados/escala_gerada_{instancia}_GA.csv", index=False
            )

            print("[OK] GA Concluído!")
            print(f"     -> Tempo: {tempo_ga:.3f} segundos")
            print(f"     -> Pico de RAM: {memoria_pico_mb:.3f} MB")
            print(f"     -> Custo: {custo_ga}")

        except Exception as e:
            print(f"[FALHA CRÍTICA] Erro no GA para {instancia}: {e}")
            custo_ga, tempo_ga, memoria_pico_mb = "Erro", 0.0, 0.0
            if tracemalloc.is_tracing():
                tracemalloc.stop()

        # --- 2. EXECUÇÃO DO SOLVER EXATO (PLI) ---
        print("\n[>>] Iniciando Programação Linear Inteira (PLI)...")
        tracemalloc.start()
        start_time_pli = time.time()

        try:
            # 1. Chama a função dele travando a flag de salvar arquivos (save_results=False)
            escala_pli, custo_pli, tempo_interno_pli = solver_PLI(
                instancia=instancia,
                timeLimit_per_shift=30,
                verbose=False,
                save_results=False,
            )

            # 2. Desliga os sensores
            tempo_pli = time.time() - start_time_pli
            current_mem, peak_mem = tracemalloc.get_traced_memory()
            tracemalloc.stop()
            memoria_pico_pli_mb = peak_mem / (1024 * 1024)

            # 3. VOCÊ salva o arquivo na SUA pasta de resultados
            escala_pli.to_csv(
                f"resultados/escala_gerada_{instancia}_PLI.csv", index=False
            )

            print("[OK] PLI Concluído!")
            print(f"     -> Tempo: {tempo_pli:.3f} segundos")
            print(f"     -> Pico de RAM: {memoria_pico_pli_mb:.3f} MB")
            print(f"     -> Custo: {custo_pli}")

        except Exception as e:
            print(f"[FALHA CRÍTICA] Erro no PLI para {instancia}: {e}")
            custo_pli, tempo_pli, memoria_pico_pli_mb = "Erro", 0.0, 0.0
            if tracemalloc.is_tracing():
                tracemalloc.stop()

        resultados.append(
            {
                "Instancia": instancia,
                "Custo_GA": custo_ga,
                "Tempo_GA_s": round(tempo_ga, 3),
                "Memoria_Pico_GA_MB": round(memoria_pico_mb, 3),
                "Custo_PLI": custo_pli,
                "Tempo_PLI_s": round(tempo_pli, 3),
                "Memoria_Pico_PLI_MB": round(memoria_pico_pli_mb, 3),
            }
        )

    # Imprime a tabela final
    df_resultados = pd.DataFrame(resultados)
    print("\n" + "=" * 60)
    print(df_resultados.to_string(index=False))

    df_resultados.to_csv("analise_comparativa_final.csv", index=False)
    print(
        "\n[SUCESSO] Resultados consolidados salvos em 'analise_comparativa_final.csv'."
    )


if __name__ == "__main__":
    # O lote de instâncias definido para a análise
    instancias_alvo = ["i01", "i02", "i03", "i04", "i06"]

    run_comparative_analysis(instancias_alvo)
