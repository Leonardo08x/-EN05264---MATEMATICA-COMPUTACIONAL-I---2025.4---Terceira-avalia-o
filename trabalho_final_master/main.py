import asyncio
from metaheuristica.GA import algoritmo_genetico
from solver.solve import solver
from concurrent.futures import ProcessPoolExecutor

async def main():
 with ProcessPoolExecutor() as executor:
    loop = asyncio.get_running_loop()
    for i in range(1, 31):
        dia = f"i0{i}" if i < 10 else f"i{i}"

        # garante que as duas funções sejam executadas simultaneamente, programação em paralelo
        await asyncio.gather(
            loop.run_in_executor(executor,algoritmo_genetico, dia),
            loop.run_in_executor(executor,solver,dia)
        )

if __name__ == "__main__":
 try:
    asyncio.run(main())
 except Exception as e:
    print(f"Ocorreu um erro: {e}")