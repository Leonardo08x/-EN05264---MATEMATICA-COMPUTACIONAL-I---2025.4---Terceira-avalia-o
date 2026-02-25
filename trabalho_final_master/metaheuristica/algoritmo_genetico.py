"""
Módulo do Algoritmo Genético (Metaheurística)
Abordagem: Otimização Gulosa por Turno (Shift-by-Shift)
"""

from email import utils

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
    # max_load no dataset dita o limite de peso acumulado que o enfermeiro suporta
    enfermeiros_unicos = df_nurses.drop_duplicates("nurse_id")
    nurse_skills = enfermeiros_unicos.set_index("nurse_id")["skill_level"].to_dict()
    nurse_max_load = enfermeiros_unicos.set_index("nurse_id")["max_load"].to_dict()

    # Inicia todo mundo com 0 de carga de trabalho acumulada na semana
    nurse_workload = {nurse: 0 for nurse in nurse_skills.keys()}

    # 3. Pré-processamento O(1)
    turnos_nurses = df_nurses.groupby("global_shift")
    turnos_rooms = df_rooms.groupby("global_shift")
    todos_turnos = sorted(df_rooms["global_shift"].unique())

    escala_final = []
    custo_total_acumulado = 0

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

        # Removido o bloqueio de falta de enfermeiros. O algoritmo vai ter que se virar
        # para alocar o mesmo enfermeiro em vários quartos.

        # --- A FUNÇÃO DE FITNESS (O ORÁCULO) ---
        class NRAPerShift(Problem):
            def __init__(self, bounds=None, minmax="min", **kwargs):
                super().__init__(bounds, minmax, **kwargs)

            def obj_func(self, solution):
                # 'solution' agora é um vetor de inteiros onde o índice é o Quarto e o valor é o Enfermeiro
                custo_turno = 0

                # Memória volátil: para saber quanto de carga o enfermeiro está recebendo SÓ NESTE TURNO
                carga_recebida_neste_turno = {enf: 0 for enf in enfermeiros_disponiveis}

                for i in range(num_quartos):
                    quarto = quartos_hoje[i]
                    idx_enf = int(solution[i])
                    enf_id = enfermeiros_disponiveis[idx_enf]

                    # Penalidade 1: S2_room_nurse_skill (Déficit de Habilidade)
                    req_skill = quarto["max_skill_required"]
                    enf_skill = nurse_skills[enf_id]
                    if enf_skill < req_skill:
                        custo_turno += (req_skill - enf_skill) * pesos.get(
                            "S2_room_nurse_skill", 10
                        )

                    # Acumula a carga que o enfermeiro pegou na simulação deste indivíduo
                    carga_recebida_neste_turno[enf_id] += quarto["total_room_workload"]

                # Penalidade 2: S4_nurse_excessive_workload (Excesso de Carga Horária Global)
                # Verifica se o que ele pegou HOJE somado ao que ele já tinha na SEMANA estoura o contrato
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
        # AQUI ESTÁ A MÁGICA: Cada quarto (gene) sorteia um ID de enfermeiro (de 0 a num_enfermeiros - 1)
        # Sendo um IntegerVar e não uma PermutationVar, a repetição é nativa e permitida.
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

        # --- DECODIFICAÇÃO E ATUALIZAÇÃO DA MEMÓRIA GLOBAL ---
        carga_efetivada = {enf: 0 for enf in enfermeiros_disponiveis}

        for i in range(num_quartos):
            idx_enf = int(best_solution[i])
            enf_id = enfermeiros_disponiveis[idx_enf]
            quarto = quartos_hoje[i]

            # Registra na Escala
            escala_final.append(
                {
                    "global_shift": turno,
                    "room_id": quarto["room_id"],
                    "nurse_id": enf_id,
                }
            )

            # Acumula a carga real que foi decidida
            carga_efetivada[enf_id] += quarto["total_room_workload"]

        # Aplica a carga de trabalho física no histórico global da semana
        for enf_id, carga in carga_efetivada.items():
            if carga > 0:
                nurse_workload[enf_id] += carga

        print(
            f"  > Turno {turno:02d} resolvido | Custo Local: {best_cost} | Quartos alocados: {num_quartos}"
        )

    df_escala = pd.DataFrame(escala_final)
    print(f"\n[FIM] Custo Total Ponderado (S2 + S4): {custo_total_acumulado}")

    return df_escala, custo_total_acumulado


# ==========================================
# CÓDIGO DE TESTE
# ==========================================
if __name__ == "__main__":
    for i in range(1, 3):
        dia = f"i{i:02d}"

        escala, custo = algoritmo_genetico(dia)
        print("\nEscala Gerada (Primeiras 10 alocações):")

        if not escala.empty:
            print(escala.head(10))
            utils.save_results(dia, escala)

        else:
            print("A escala retornou vazia. Verifique os logs.")
