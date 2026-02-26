import time
import pandas as pd
import pulp
from typing import Tuple
from utils import utils

"""
O algoritmo PLI (Programação Linear Inteira) é uma 
técnica de otimização que busca encontrar a melhor solução viavel para um problema, 
onde as variáveis de decisão são restritas a valores inteiros. 
No contexto do problema de escala de enfermeiros, 
o PLI pode ser utilizado para alocar enfermeiros a quartos de forma a 
minimizar penalidades associadas à falta de habilidade e excesso de carga de trabalho.
A função solver_PLI é responsável por resolver 
o problema de escala de enfermeiros utilizando o PLI.
Ela recebe como entrada a instância do problema,
um limite de tempo para resolver cada turno
Retorna: (df_escala, custo_total_acumulado, temp_total)
"""


def solver_PLI(
    instancia: str,  # nome da instância a ser resolvida
    timeLimit_per_shift: int = 30,  # limite de tempo em segundos para resolver cada turno
    verbose: bool = True,  # bool imprimir mensagens de progresso
    save_results: bool = False,  # bool salvar os resultados em arquivo CSV
) -> Tuple[
    pd.DataFrame, float, float
]:  # retorna a escala final, o custo total acumulado e o tempo total em segundos

    if verbose:
        print(f"\n[INÍCIO] Resolvendo instância NRA: {instancia}")

    # inicia medição do tempo total
    t_start_total = time.time()

    # 1. Carregamento dos dados
    # A utils dataset_info retorna;
    #  A) os pesos completos do problema (incluindo S2 e S4),
    #  B) o dataframe de enfermeiros,
    #  C) dataframe de quartos.
    pesos_full, df_enfermeiros, df_salas = utils.dataset_info(instancia)

    # 2. Extração dos pesos
    #
    pesos = pesos_full.get("weights", {})
    W_skill = pesos.get("S2_room_nurse_skill", 10)
    W_work = pesos.get("S4_nurse_excessive_workload", 10)

    # 3. Mapas de Habilidade e Carga Máxima
    enfermeiros_unicos = df_enfermeiros.drop_duplicates("nurse_id")
    nurse_skill_map = enfermeiros_unicos.set_index("nurse_id")["skill_level"].to_dict()
    nurse_load_map = enfermeiros_unicos.set_index("nurse_id")["max_load"].to_dict()

    # Agrupamento por turno global
    turnos_nurses = df_enfermeiros.groupby("global_shift")
    turnos_rooms = df_salas.groupby("global_shift")
    todos_turnos = sorted(df_salas["global_shift"].unique())

    escala_final = []
    custo_total_acumulado = 0.0

    #
    # ---------- ABORDAGEM: OTIMIZAÇÃO GULOSA POR TURNO (DECOMPOSIÇÃO TEMPORAL) ----------
    # 4. Processamento Turno a Turno

    """
    a cada turno, o modelo PLI é construído do zero,
    garantindo que ele lide apenas com os dados relevantes daquele turno específico.

    VANTAGENS: Isso reduz drasticamente o número de variáveis e restrições,
    tornando o problema mais manejável e acelerando a resolução.

    DESVANTAGENS: O modelo PLI é resolvido de forma sequencial, turno a turno,
    o que pode aumentar o tempo total de execução, especialmente se houver muitos turnos.


    Pipeline do código:

    [INÍCIO] → Loop turnos → Filtrar dados turno → Criar modelo MILP 
    → Criar variáveis → Definir objetivo → Adicionar restrições → Resolver (solver) → 
    Extrair solução → Somar custo → Próximo turno → Gerar resultado final → [FIM]"""

    for turno in todos_turnos:
        if verbose:
            print(f"  > Otimizando Turno Global {turno}...", end="\r")

        # Filtra os dados do turno atual
        # esse passo é realizado para evitar que o modelo PLI
        # tenha que lidar com dados irrelevantes que seriam de outros turnos,
        # o que pode aumentar significativamente o tempo de resolução.
        quartos_turno = turnos_rooms.get_group(turno).reset_index(drop=True)

        if turno not in turnos_nurses.groups:
            continue

        nurses_disponiveis = turnos_nurses.get_group(turno)
        lista_nurses = nurses_disponiveis["nurse_id"].tolist()

        # Modelo PLI (Minimização)
        # pulp.LpProblem é a classe que representa o modelo de otimização.
        # O primeiro argumento é o nome do problema (usado para identificação e depuração).
        # O segundo argumento é o tipo de problema, que pode ser pulp.LpMinimize para minimização
        # ou pulp.LpMaximize para maximização.
        prob = pulp.LpProblem(f"NRA_Turno_{turno}", pulp.LpMinimize)

        # VARIÁVEIS DE DECISÃO (int or binary)
        # exemplo: x[(n, r)] = 1 se enfermeiro n for alocado ao quarto r, 0 caso contrário
        x = pulp.LpVariable.dicts(
            "x",
            ((n, r) for n in lista_nurses for r in quartos_turno.index),
            cat="Binary",
        )

        # z: Excesso de carga : int
        # exemplo: z[n] representa o excesso de carga do enfermeiro n,
        #  que é a quantidade de carga que ele recebe além de sua capacidade máxima.
        z = pulp.LpVariable.dicts("z", lista_nurses, lowBound=0, cat="Integer")

        # FUNÇÃO OBJETIVO: S2 (Déficit Habilidade) + S4 (Excesso Carga)
        # A função objetivo é a soma ponderada das penalidades S2 e S4, onde:
        # S2: Para cada quarto, se o enfermeiro alocado tiver habilidade inferior à requerida,
        # é calculada uma penalidade proporcional à diferença de habilidade multiplicada pelo peso W
        # S4: Para cada enfermeiro, se a carga total atribuída a ele exceder sua capacidade máxima,
        # é calculada uma penalidade proporcional ao excesso de carga multiplicada pelo peso W

        penalidades = []

        # Penalidade S2
        for n in lista_nurses:
            n_skill = nurse_skill_map.get(n, 0)
            for r_idx in quartos_turno.index:
                r_row = quartos_turno.loc[r_idx]
                # Deficit é fixo: max(0, requerido - possui)
                deficit = max(0, int(r_row["max_skill_required"]) - int(n_skill))
                if deficit > 0:
                    penalidades.append(x[(n, r_idx)] * (W_skill * deficit))

        # Penalidade S4
        for n in lista_nurses:
            penalidades.append(z[n] * W_work)

        prob += pulp.lpSum(penalidades)

        # RESTRIÇÕES
        # 1. Cobertura: Cada quarto ocupado precisa de EXATAMENTE 1 enfermeiro
        for r_idx in quartos_turno.index:
            alocacoes_quarto = [x[(n, r_idx)] for n in lista_nurses]
            soma_alocacoes = pulp.lpSum(alocacoes_quarto)
            prob += soma_alocacoes == 1

        # 2. Excesso de Trabalho: Carga Total - Carga Máxima <= z
        for n in lista_nurses:
            # Soma das cargas dos quartos atribuídos ao enfermeiro n
            carga_atribuida = pulp.lpSum(
                x[(n, r_idx)] * float(quartos_turno.loc[r_idx, "total_room_workload"])
                for r_idx in quartos_turno.index
            )

            cap_maxima = float(nurse_load_map.get(n, 0))
            prob += carga_atribuida - cap_maxima <= z[n]

        # RESOLUÇÃO BRANCH AND BOUND COM LIMITE DE TEMPO
        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=timeLimit_per_shift)
        prob.solve(solver)

        # EXTRAÇÃO DOS RESULTADOS
        if pulp.LpStatus[prob.status] in ["Optimal", "Integer Feasible"]:
            custo_total_acumulado += pulp.value(prob.objective)
            for r_idx, r_row in quartos_turno.iterrows():
                for n in lista_nurses:
                    if pulp.value(x[(n, r_idx)]) > 0.5:
                        escala_final.append(
                            {
                                "global_shift": int(turno),
                                "room_id": r_row["room_id"],
                                "nurse_id": n,
                            }
                        )
                        break

    # 5. RESULTADO FINAL
    df_escalaenf = pd.DataFrame(escala_final)

    if save_results:
        utils.save_results(instancia, df_escalaenf)

    t_end_total = time.time()
    temp_total = t_end_total - t_start_total

    if verbose:
        print(f"\n[FIM] Custo Total Acumulado: {custo_total_acumulado:.2f}")
        print(f"[TEMPO] Tempo total de execução: {temp_total:.2f} s")

    return df_escalaenf, custo_total_acumulado, temp_total


"""
EXEMPLO TESTE I04 COM PLI
O teste abaixo é um exemplo de como chamar a função solver_PLI para resolver a instância
Como usar:
    1. Certifique-se de que a instância "i04" esteja presente na pasta dataset/dataset/i04
    2. Execute este script. Ele irá resolver a instância usando o PLI e imprimir os resultados.
    3. O resultado inclui o número de linhas na escala gerada, o custo total
        acumulado e o tempo gasto para resolver a instância.
    Observação: O tempo reportado pelo solver é o tempo gasto apenas na resolução do modelo PLI,
    enquanto o tempo medido pelo sistema inclui todo o processo,
    desde o carregamento dos dados até a geração do resultado final.
    """


def teste_solver():
    instancia = "i04"  # troque pela instância que quiser testar
    limite_tempo = 10  # segundos por turno

    print("\n===== TESTE DO SOLVER PLI =====\n")

    t0 = time.time()

    df, custo, tempo_total = solver_PLI(
        instancia=instancia,
        timeLimit_per_shift=limite_tempo,
        verbose=True,
        save_results=False,
    )

    t1 = time.time()

    print("\n===== RESULTADOS =====")
    print("Instância:", instancia)
    print("Linhas da escala:", len(df))
    print("Custo total:", custo)
    print("Tempo reportado solver:", round(tempo_total, 4), "s")
    print("Tempo medido sistema:", round(t1 - t0, 4), "s")


if __name__ == "__main__":
    teste_solver()

    # Comentarios finais:
    # o solver funciona da seguinte forma:
    # 1. Carrega os dados da instância usando a função dataset_info da utils.
    # 2. Extrai os pesos S2 e S4 do dicionário de pesos
    # 3. Cria mapas de habilidade e carga máxima dos enfermeiros para acesso rápido.
    # 4. Agrupa os dados por turno global para facilitar o processamento turno a turno.
    # 5. Para cada turno, filtra os dados relevantes e constrói um modelo PLI específico para aquele turno.
    # 6. Define as variáveis de decisão, a função objetivo e as restrições do modelo.
    # 7. Resolve o modelo usando o solver CBC com um limite de tempo por turno.
    # 8. Extrai a solução e acumula o custo total.
    # 9. Ao final, gera um DataFrame com a escala final, imprime o custo total acumulado e o tempo gasto.
