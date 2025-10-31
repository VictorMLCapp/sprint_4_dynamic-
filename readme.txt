# Sprint 4  

**FIAP — Engenharia de Software**

Projeto final da Sprint 4 com foco em **Programação Dinâmica** aplicada ao problema de **controle e reposição de insumos hospitalares**. O sistema modela e resolve o problema usando **estruturas de dados clássicas** (fila, pilha, buscas, ordenações) e **modelagem dinâmica** para reduzir desperdícios e melhorar a previsibilidade de consumo.

---

## 🎯 Objetivo

Nas unidades de diagnóstico, o consumo de insumos (reagentes e descartáveis) não é registrado com precisão, o que dificulta o controle de estoque e a previsão de reposição. A proposta desta sprint é:

> Modelar o problema utilizando **Programação Dinâmica**, formulando estados, decisões e função objetivo para minimizar custos e desperdícios no estoque.

---

## 🧩 Formulação do Problema (70 pts)

### 1️⃣ Estados e Decisões

* **Estado (t, s)** → representa o **dia t** e o **nível de estoque s**.
* **Decisão (q_t)** → quantidade de unidades a repor no início do dia `t`.

### 2️⃣ Função de Transição

```
s' = max(0, s + q_t − demanda[t])
falta = max(0, demanda[t] − (s + q_t))
```

### 3️⃣ Função Objetivo

Minimizar o custo total ao longo do horizonte de tempo `T`:

```
Custo total = Σ (c*q_t + h*s' + p*falta)
```

Onde:

* `c` = custo por unidade comprada
* `h` = custo por armazenagem
* `p` = penalidade por falta

### 4️⃣ Abordagens

* **Top-Down (Recursiva com Memoização)** — versão otimizada com cache de resultados.
* **Bottom-Up (Iterativa)** — tabela dinâmica preenchida do fim para o início do horizonte.
* Ambas são testadas para **produzir resultados idênticos** (validação obrigatória).

---

## 🧮 Estruturas de Dados Clássicas

| Requisito            | Implementação | Descrição                                                       |
| -------------------- | ------------- | --------------------------------------------------------------- |
| **Fila (FIFO)**      | ✅             | Armazena consumo diário em ordem cronológica                    |
| **Pilha (LIFO)**     | ✅             | Permite consultas em ordem inversa (consumos recentes primeiro) |
| **Busca Sequencial** | ✅             | Pesquisa item específico em toda a lista                        |
| **Busca Binária**    | ✅             | Pesquisa otimizada após ordenação por nome                      |
| **Merge Sort**       | ✅             | Ordena registros por quantidade ou validade                     |
| **Quick Sort**       | ✅             | Ordena registros decrescentemente por consumo                   |

---

## ⚙️ Execução

### Requisitos

* **Python 3.9+** instalado.

### Como Rodar

```bash
python sprint.py
```

### Menu Principal

```
1) Simular consumo (gera registros)
2) Ver Fila (FIFO)
3) Ver Pilha (LIFO)
4) Buscar item (Sequencial/Binária)
5) Ordenar (quantidade/validade)
6) Gerar Relatório
7) Otimizar Reposição (Programação Dinâmica)
8) Ajustar Parâmetros (c, h, p, Qmax, Smax)
0) Sair
```

---

## 📊 Saída e Relatório

Após a execução, é gerado automaticamente o arquivo:

```
relatorio_dynamic_programming.txt
```

O relatório inclui:

* Estoque atual e ideal por setor
* Produtos faltantes ou excedentes
* Estruturas de dados utilizadas
* Formulação da PD
* Política ótima de reposição (q_t)
* Custos e equivalência entre versões recursiva e iterativa

---

## 📁 Estrutura do Projeto

```
📦 Sprint4_DynamicProgramming
 ├── sprint.py                     # Código principal
 ├── relatorio_dynamic_programming.txt   # Relatório gerado
 └── README.md                    # Este arquivo
```

---

## 📈 Resultado Esperado

* Solução completa com **estruturação eficiente de dados**
* **Formulação matemática e prática** da Programação Dinâmica
* Relatório documentado e pronto para GitHub
* Pontuação total: **100 pts** 💯🔥

---

## 👤 Autor

**Nomes:** Victor Mattenhauer Lopes Capp - RM 555753
          Igor Brunelli Ralo - RM 555035
          Artur Alves Tenca - RM 555171
**Curso:** Engenharia de Software — FIAP
**Sprint:** 4 — Programação Dinâmica
