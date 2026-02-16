import geneticalgorithm as ga
import numpy as np
from utils.utils import dataset_info
#dataframe é chamado na função
def algoritmo_genetico(dia):
    print(f"Processando o algoritmo genético para o dia {dia}...")
    pesos, turno_enfermeiras, quartos = dataset_info(dia)
    
    #print(f"Dataset {dia} carregado com sucesso!")
    #print(f"Pesos: {pesos}")
    #print(f"Turno das enfermeiras:\n{turno_enfermeiras.head()}")
    #print(f"Quartos ocupados:\n{quartos.head()}")