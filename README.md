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

**UFPA - ICEN - FACOM**P  
**Disciplina:** EN05264 - MATEMÁTICA COMPUTACIONAL 1  
**Docentes:** Claudomiro Sales e Helder Matos

---

## Tecnologias e Abordagens

O projeto implementa e compara duas metodologias distintas:

1. PLI (Programação Linear Inteira): Formulação matemática exata utilizando variáveis binárias ou inteiras.
2. Metaheurística (Algoritmo Genético): Implementação estocástica para busca de soluções e análise de comportamento médio.

## Como Executar

O projeto utiliza asyncio e ProcessPoolExecutor para garantir a execução simultânea das abordagens e otimizar o tempo de coleta de resultados.

**OBS:** Descompacte o dataset.zip pois o programa espera pastas nesse formato na pasta dataset: *dataset/i01/arquivo.json*

1. Bibliotecas Necessárias:
   * pandas (Manipulação de dados CSV)
   * numpy (Operações matemáticas)
   * mealpy (Implementação da metaheurística)
   * matplotlib (Visualização de gráficos)

2. Configuração do Ambiente (Recomendado):

   ```bash
   python -m venv .venv

   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```

3. Instalação:

   ```bash
   pip install -r requirements.txt
   ```

4. Execução:

   ```bash
   cd trabalho_final_master
   
   python -m main.py
   ```

## Prazo de Entrega

* Deadline: 26 de fevereiro de 2026.
