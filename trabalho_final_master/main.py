"""
Módulo principal
"""

import asyncio
from trabalho_final_master.metaheuristica.algoritmo_genetico import algoritmo_genetico
from solver.solve import solver
from concurrent.futures import ProcessPoolExecutor


async def main():
	"""
    Função principal para executar o projeto
	"""
    with ProcessPoolExecutor() as executor:
        loop = asyncio.get_running_loop()
        for i in range(1, 31):
            instancia = f"i0{i}" if i < 10 else f"i{i}"

            # garante que as duas funções sejam executadas simultaneamente, programação em paralelo
            await asyncio.gather(
                loop.run_in_executor(executor, algoritmo_genetico, instancia),
                loop.run_in_executor(executor, solver, instancia),
            )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:

        print(f"Ocorreu um erro: {e}")
