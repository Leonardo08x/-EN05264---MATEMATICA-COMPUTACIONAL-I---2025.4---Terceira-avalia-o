import pandas as pd
import json

def dataset_info(dia):
    pesos = json.load(open(f"dataset/{dia}/instance_info.json"))
    turno_enfermeiras = pd.read_csv(f"dataset/{dia}/nurse_shifts.csv")
    quartos = pd.read_csv(f"dataset/{dia}/occupied_room_shifts.csv")
    return pesos, turno_enfermeiras, quartos