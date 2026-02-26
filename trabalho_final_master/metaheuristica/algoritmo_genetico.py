"""
Módulo do Algoritmo Genético (Metaheurística)
Abordagem: Otimização Gulosa por Turno (Shift-by-Shift)
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mealpy.evolutionary_based import GA
from mealpy import IntegerVar, Problem
import warnings

# Suprimir avisos verbosos da biblioteca para manter o log limpo
warnings.filterwarnings("ignore")

from utils import utils


def algoritmo_genetico(instancia):
    print(
        f"\n[INIT] Inicializando GA (Modo Otimização por Turno) para a instância: {instancia}"
    )

    # 1. Ingestão de Dados via Parser
    pesos, df_nurses, df_rooms = utils.dataset_info(instancia)

    # 2. O Gerenciador de Estado Global (A Memória)
    enfermeiros_unicos = df_nurses.drop_duplicates("nurse_id")
    nurse_skills = enfermeiros_unicos.set_index("nurse_id")["skill_level"].to_dict()
    nurse_max_load = enfermeiros_unicos.set_index("nurse_id")["max_load"].to_dict()

    nurse_workload = {nurse: 0 for nurse in nurse_skills.keys()}

    # 3. Pré-processamento O(1)
    turnos_nurses = df_nurses.groupby("global_shift")
    turnos_rooms = df_rooms.groupby("global_shift")
    todos_turnos = sorted(df_rooms["global_shift"].unique())

    escala_final = []
    custo_total_acumulado = 0
    historico_convergencia_global = []  # Armazena a curva de aprendizado de cada turno

    # --- LOOP DO MAESTRO ---
    for turno in todos_turnos:
        quartos_hoje = turnos_rooms.get_group(turno).to_dict("records")

        if turno not in turnos_nurses.groups:
            continue

        enfermeiros_disponiveis = turnos_nurses.get_group(turno)["nurse_id"].tolist()
        num_quartos = len(quartos_hoje)
        num_enfermeiros = len(enfermeiros_disponiveis)

        if num_quartos == 0 or num_enfermeiros == 0:
            continue

        # --- A FUNÇÃO DE FITNESS (O ORÁCULO) ---
        class NRAPerShift(Problem):
            def __init__(self, bounds=None, minmax="min", **kwargs):
                super().__init__(bounds, minmax, **kwargs)

            def obj_func(self, solution):
                custo_turno = 0
                carga_recebida_neste_turno = {enf: 0 for enf in enfermeiros_disponiveis}

                for i in range(num_quartos):
                    quarto = quartos_hoje[i]
                    idx_enf = int(solution[i])
                    enf_id = enfermeiros_disponiveis[idx_enf]

                    # S2: Déficit de Habilidade
                    req_skill = quarto["max_skill_required"]
                    enf_skill = nurse_skills[enf_id]
                    if enf_skill < req_skill:
                        custo_turno += (req_skill - enf_skill) * pesos.get(
                            "S2_room_nurse_skill", 10
                        )

                    carga_recebida_neste_turno[enf_id] += quarto["total_room_workload"]

                # S4: Excesso de Carga Global
                for enf_id, carga_extra in carga_recebida_neste_turno.items():
                    if carga_extra > 0:
                        load_simulada = nurse_workload[enf_id] + carga_extra
                        max_l = nurse_max_load[enf_id]
                        if load_simulada > max_l:
                            custo_turno += (load_simulada - max_l) * pesos.get(
                                "S4_nurse_excessive_workload", 10
                            )

                return custo_turno

        # --- EXECUÇÃO DO ALGORITMO GENÉTICO ---
        bounds = [
            IntegerVar(lb=0, ub=num_enfermeiros - 1, name=f"Q_{i}")
            for i in range(num_quartos)
        ]
        problem = NRAPerShift(bounds=bounds, minmax="min")

        model = GA.BaseGA(epoch=50, pop_size=40)
        model.solve(problem)

        best_solution = model.g_best.solution
        best_cost = model.g_best.target.fitness
        custo_total_acumulado += best_cost

        # Extrai a curva de convergência deste turno específico
        historico_turno = [sol.target.fitness for sol in model.history.list_global_best]
        historico_convergencia_global.append(historico_turno)

        # --- DECODIFICAÇÃO E ATUALIZAÇÃO DA MEMÓRIA GLOBAL ---
        carga_efetivada = {enf: 0 for enf in enfermeiros_disponiveis}

        for i in range(num_quartos):
            idx_enf = int(best_solution[i])
            enf_id = enfermeiros_disponiveis[idx_enf]
            quarto = quartos_hoje[i]

            escala_final.append(
                {
                    "global_shift": turno,
                    "room_id": quarto["room_id"],
                    "nurse_id": enf_id,
                }
            )
            carga_efetivada[enf_id] += quarto["total_room_workload"]

        for enf_id, carga in carga_efetivada.items():
            if carga > 0:
                nurse_workload[enf_id] += carga

        print(
            f"  > Turno {turno:02d} resolvido | Custo Local: {best_cost} | Quartos alocados: {num_quartos}"
        )

    df_escala = pd.DataFrame(escala_final)
    print(
        f"\n[FIM] Custo Total Ponderado Instância {instancia}: {custo_total_acumulado}"
    )

    # --- GERAÇÃO DO GRÁFICO DE CONVERGÊNCIA ---
    if historico_convergencia_global:
        matriz_historico = np.array(historico_convergencia_global)
        convergencia_media = np.mean(matriz_historico, axis=0)

        plt.figure(figsize=(10, 6))
        plt.plot(
            convergencia_media,
            color="#1f77b4",
            linewidth=2.5,
            label="Custo Médio (Fitness)",
        )
        plt.title(
            f"Convergência Média por Turno - GA Guloso (Instância {instancia})",
            fontsize=14,
        )
        plt.xlabel("Gerações (Epochs)", fontsize=12)
        plt.ylabel("Custo Médio de Penalidades (S2 + S4)", fontsize=12)
        plt.grid(True, linestyle="--", alpha=0.7)
        plt.legend(fontsize=12)

        nome_imagem = f"resultados/convergencia_{instancia}_GA.png"
        plt.savefig(nome_imagem, bbox_inches="tight")
        plt.close()
        print(f"[SUCESSO] Gráfico de convergência salvo como '{nome_imagem}'.")

    return df_escala, custo_total_acumulado


# ==========================================
# CÓDIGO DE TESTE AUTOMATIZADO (LOTE DE INSTÂNCIAS)
# ==========================================
if __name__ == "__main__":
    # Lista com as 4 instâncias que você deseja testar
    instancias_teste = ["i01", "i02", "i03", "i04", "i06"]

    for instancia in instancias_teste:
        print(f"\n{'='*60}")
        print(f"INICIANDO PROCESSAMENTO AUTOMATIZADO: Instância {instancia}")
        print(f"{'='*60}")

        try:
            escala, custo = algoritmo_genetico(instancia)

            # Salvar CSV das escalas com segurança na raiz para evitar erros de diretório
            nome_csv = f"resultados/escala_gerada_{instancia}_GA.csv"
            escala.to_csv(nome_csv, index=False)
            print(f"[SUCESSO] Escala salva como '{nome_csv}'.")

        except FileNotFoundError:
            print(
                f"[ERRO] Arquivos da instância {instancia} não encontrados. Verifique se a pasta dataset/{instancia} existe."
            )
        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha na instância {instancia}: {str(e)}")

    print(
        "\n[FINALIZADO] Processamento em lote concluído. Verifique os gráficos (.png) e escalas (.csv) na pasta."
    )
