from utils.utils import dataset_info


def solver(dia):
    print(f"Processando o solver para o dia {dia}...")
    pesos, turno_enfermeiras, quartos = dataset_info(dia)
    
    #print(f"Dataset {dia} carregado com sucesso!")
    #print(f"Pesos: {pesos}")
    #print(f"Turno das enfermeiras:\n{turno_enfermeiras.head()}")
    #print(f"Quartos ocupados:\n{quartos.head()}")