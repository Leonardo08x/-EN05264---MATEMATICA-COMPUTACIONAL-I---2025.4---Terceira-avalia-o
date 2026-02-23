"""
Módulo para estrutura do solver (exatidão)
"""

from utils.utils import dataset_info


def solver(instancia):
    print(f"Processando o solver para o instancia {instancia}...")
    pesos, turno_enfermeiras, quartos = dataset_info(instancia)

    # print(f"Dataset {instancia} carregado com sucesso!")
    # print(f"Pesos: {pesos}")
    # print(f"Turno das enfermeiras:\n{turno_enfermeiras.head()}")

    # print(f"Quartos ocupados:\n{quartos.head()}")
