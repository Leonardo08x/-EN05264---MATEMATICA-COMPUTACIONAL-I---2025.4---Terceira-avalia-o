# Integrated Healthcare Timetabling - NRA Solver (IHTP-2024)

Este repositório contém o desenvolvimento do projeto final para a disciplina de Matemática Computacional I (UFPA / ICEN / FACOMP), focado na resolução do problema de Alocação de Enfermeiro por Quarto (Nurse-to-Room Assignment - NRA). O objetivo é realizar a alocação de exatamente um enfermeiro para cada quarto ocupado em cada turno, respeitando as escalas fixas de trabalho e buscando minimizar penalidades de custo.

## Sobre o Problema

O NRA é um subproblema da competição Integrated Healthcare Timetabling Competition 2024 (IHTC-2024).

### Restrições e Penalidades

* Cobertura: Para cada turno e quarto ocupado, deve haver exatamente um enfermeiro designado.
* Disponibilidade: O enfermeiro deve estar em serviço no turno conforme sua escala fixa.
* Déficit de Habilidade (Penalidade): Aplicada quando o nível de habilidade do enfermeiro é inferior ao exigido pelos pacientes no quarto.
* Excesso de Trabalho (Penalidade): Aplicada quando a soma da carga de trabalho dos quartos atribuídos a um enfermeiro excede sua capacidade no turno.

## UFPA - ICEN - FACOMP

* **Disciplina:** Matemática Computacional 1 (EN05264)
* **Docentes:** Claudomiro Sales e Helder Matos  
* **Equipe:**
  * Alessandro Reali Lopes Silva
  * Felipe Lisboa Brasil
  * Leonardo Cunha da Rocha

---

## Tecnologias e Abordagens

O projeto implementa e compara duas metodologias distintas:

1. PLI (Programação Linear Inteira): Formulação matemática exata utilizando variáveis binárias ou inteiras.
2. Metaheurística (Algoritmo Genético): Implementação estocástica com abordagem gulosa (Shift-by-Shift) para busca de soluções e análise de trade-off (Qualidade vs. Tempo).

## Como Executar

O orquestrador do projeto (main.py) executa ambas as abordagens (GA e PLI) de forma sequencial para as instâncias configuradas, extraindo métricas de tempo de CPU, pico de RAM e custo total para fins de benchmark.

### [ATENÇÃO] Pré-requisito de Dados

* Descompacte o arquivo dataset.zip dentro de `trabalho_final_master/`. A estrutura física de diretórios deve ficar estritamente neste formato: `trabalho_final_master/dataset/i01/instance_info.json`
* A versão do Python utilizada para desenvolvimento e testes é a 3.10. Certifique-se de ter esta versão instalada, obedecendo o que está especificado no arquivo `.python-version`.

### 1. Bibliotecas Necessárias

* pandas (Manipulação de dados CSV)
* numpy (Operações matemáticas)
* mealpy (Implementação da metaheurística)
* matplotlib (Visualização de gráficos de convergência)
* pulp (Modelagem e execução do solver PLI)

### 2. Configuração do Ambiente Virtual (Recomendado)

É fortemente recomendado isolar as dependências em um ambiente virtual. No terminal, na raiz do projeto, digite:

```bash
python -m venv .venv

```

* Para ativar o ambiente (Linux/Mac)

   ```bash
   source .venv/bin/activate

   ```

* Para ativar o ambiente (Windows):

   ```bash
   .venv\Scripts\activate

   ```

### 3. Instalação de Dependências

Com o ambiente ativado, instale todos os pacotes necessários através do manifesto:

```bash
pip install -r requirements.txt

```

### 4. Execução da Análise Comparativa

Para rodar a bateria de testes e gerar as matrizes de escala e o relatório consolidado, execute o módulo principal a partir do diretório `trabalho_final_master/` do repositório:

```bash
cd trabalho_final_master
python main.py

```

### 5. Saída de Dados (Outputs)

Após a execução, o algoritmo gerará automaticamente:

* Arquivos CSV dentro da pasta `trabalho_final_master/resultados/` com a escala de cada instância para ambos os métodos.
* Imagens em PNG dentro da pasta `trabalho_final_master/resultados/` contendo os gráficos de convergência da metaheurística.
* O arquivo `analise_comparativa_final.csv` dentro da pasta `trabalho_final_master/`, consolidando os tempos de execução, consumo de memória e custos para análise estatística.
