# Integrated Healthcare Timetabling - NRA Solver (IHTP-2024)

Este repositório contém o desenvolvimento do projeto final para a disciplina de Matemática Computacional I (UFPA / ICEN / FACOMP), focado na resolução do problema de Alocação de Enfermeiro por Quarto (Nurse-to-Room Assignment - NRA). O objetivo é realizar a alocação de exatamente um enfermeiro para cada quarto ocupado em cada turno, respeitando as escalas fixas de trabalho e buscando minimizar penalidades de custo.

## Sobre o Problema
O NRA é um subproblema da competição Integrated Healthcare Timetabling Competition 2024 (IHTC-2024).

### Restrições e Penalidades
* Cobertura: Para cada turno e quarto ocupado, deve haver exatamente um enfermeiro designado.
* Disponibilidade: O enfermeiro deve estar em serviço no turno conforme sua escala fixa.
* Déficit de Habilidade (Penalidade): Aplicada quando o nível de habilidade do enfermeiro é inferior ao exigido pelos pacientes no quarto.
* Excesso de Trabalho (Penalidade): Aplicada quando a soma da carga de trabalho dos quartos atribuídos a um enfermeiro excede sua capacidade no turno.

## Equipe
* Alessandro Reali Lopes Silva
* Felipe Lisboa Brasil
* Leonardo Cunha da Rocha

Disciplina: EN05264 - MATEMÁTICA COMPUTACIONAL I
UFPA - ICEN - FACOMP
Docentes: Claudomiro Sales e Helder Matos

---

## Tecnologias e Abordagens
O projeto implementa e compara duas metodologias distintas:
1. PLI (Programação Linear Inteira): Formulação matemática exata utilizando variáveis binárias ou inteiras.
2. Metaheurística (Algoritmo Genético): Implementação estocástica para busca de soluções e análise de comportamento médio.

## Estrutura de Pastas

## Estrutura de Pastas
📂 TRABALHO_FINAL_MASTER/
| 📂 dataset/
| 📂 metaheuristica/
│   └── 📄 GA.py
| 📂 solver/
│   └── 📄 solve.py
| 📂 utils/
│   └── 📄 utils.py
└── 📄 main.py           

---

## Como Executar
O projeto utiliza asyncio e ProcessPoolExecutor para garantir a execução simultânea das abordagens e otimizar o tempo de coleta de resultados.

1. Bibliotecas Necessárias:
   * pandas (Manipulação de dados CSV)
   * numpy (Operações matemáticas)
   * geneticalgorithm (Implementação da metaheurística)
   * asyncio (Orquestração assíncrona)

2. Instalação:
   pip install pandas numpy geneticalgorithm

3. Execução:
   python main.py

## Prazo de Entrega
* Deadline: 24 de fevereiro de 2026.
