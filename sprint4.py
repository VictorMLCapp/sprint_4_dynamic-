# =============================================================================
# SPRINT 3 — Dynamic Programming (completo)
# =============================================================================
# Este arquivo adiciona ao projeto pronto:
#  1) Formulação do problema de reposição de estoque via Programação Dinâmica
#     - Estados, decisões, transição e função objetivo (15 pts)
#  2) Duas implementações da PD
#       a) Versão recursiva com memoização (top‑down)
#       b) Versão iterativa (bottom‑up)
#     e verificação de equivalência (15 pts)
#  3) Mantém as partes já pedidas (Fila, Pilha, Buscas, Ordenações) e
#     amplia o RELATÓRIO incluindo a modelagem da PD e os resultados.
# =============================================================================

from __future__ import annotations
from collections import deque
from dataclasses import dataclass
from datetime import date, timedelta
from functools import lru_cache
from typing import List, Tuple, Dict, Callable, Any, Optional
import random
import textwrap
import os

# =============================================================================
# DADOS INICIAIS DO ESTOQUE HOSPITALAR (mesmo dataset da sprint)
# =============================================================================
estoque = {
    "Triagem": {
        "Luvas": {"quantidade": 250, "ideal": 200, "valor_unitario": 0.50, "validade": "2025-12-20"},
        "Seringas": {"quantidade": 80,  "ideal": 100, "valor_unitario": 1.00, "validade": "2025-11-05"}
    },
    "Laboratório": {
        "Tubos de ensaio": {"quantidade": 60, "ideal": 100, "valor_unitario": 2.00, "validade": "2026-01-10"},
        "Reagentes": {"quantidade": 50, "ideal": 70,  "valor_unitario": 5.00, "validade": "2025-10-25"}
    },
    "Recepção": {
        "Máscaras": {"quantidade": 170, "ideal": 150, "valor_unitario": 0.75, "validade": "2026-03-01"}
    }
}

# =============================================================================
# HELPERS
# =============================================================================

def str_to_date(yyyy_mm_dd: str) -> date:
    y, m, d = map(int, yyyy_mm_dd.split("-"))
    return date(y, m, d)

@dataclass
class Consumo:
    data: date
    setor: str
    item: str
    quantidade_consumida: int
    validade: date

    def __repr__(self):
        return (
            f"{self.data} | {self.setor} | {self.item} | "
            f"consumido={self.quantidade_consumida} | validade={self.validade}"
        )

class FilaConsumo:
    def __init__(self):
        self._fila = deque()
    def enfileirar(self, c: Consumo):
        self._fila.append(c)
    def desenfileirar(self) -> Optional[Consumo]:
        return self._fila.popleft() if self._fila else None
    def listar(self) -> List[Consumo]:
        return list(self._fila)
    def __len__(self):
        return len(self._fila)

class PilhaConsumo:
    def __init__(self):
        self._pilha: List[Consumo] = []
    def empilhar(self, c: Consumo):
        self._pilha.append(c)
    def desempilhar(self) -> Optional[Consumo]:
        return self._pilha.pop() if self._pilha else None
    def listar(self) -> List[Consumo]:
        return list(reversed(self._pilha))
    def __len__(self):
        return len(self._pilha)

# =============================================================================
# SIMULAÇÃO DE CONSUMO (mesma base da sprint)
# =============================================================================

def simular_consumo(estoque: dict, dias: int = 7, semente: int = 42) -> List[Consumo]:
    random.seed(semente)
    hoje = date.today()
    registros: List[Consumo] = []
    for d in range(dias):
        data_atual = hoje + timedelta(days=d)
        for setor, itens in estoque.items():
            for item, dados in itens.items():
                qtd_atual = dados["quantidade"]
                if qtd_atual <= 0:
                    continue
                max_consumo = max(1, int(qtd_atual * 0.10))
                consumido = random.randint(0, max_consumo)
                consumido = min(consumido, dados["quantidade"])  # não estoura
                dados["quantidade"] -= consumido
                if consumido > 0:
                    registros.append(
                        Consumo(
                            data=data_atual,
                            setor=setor,
                            item=item,
                            quantidade_consumida=consumido,
                            validade=str_to_date(dados["validade"]),
                        )
                    )
    return registros

# =============================================================================
# BUSCAS E ORDENAÇÕES (resumo — iguais à sprint anterior)
# =============================================================================

def merge_sort(arr: List[Any], key: Callable[[Any], Any]) -> List[Any]:
    if len(arr) <= 1: return arr[:]
    mid = len(arr)//2
    left = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    i=j=0; out=[]
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]): out.append(left[i]); i+=1
        else: out.append(right[j]); j+=1
    out.extend(left[i:]); out.extend(right[j:])
    return out

def quick_sort(arr: List[Any], key: Callable[[Any], Any]) -> List[Any]:
    if len(arr) <= 1: return arr[:]
    p = key(arr[len(arr)//2])
    menores = [x for x in arr if key(x) < p]
    iguais  = [x for x in arr if key(x) == p]
    maiores = [x for x in arr if key(x) > p]
    return quick_sort(menores, key) + iguais + quick_sort(maiores, key)

# =============================================================================
# ======================== PROGRAMAÇÃO DINÂMICA ===============================
# =============================================================================
# Formulação — problema de reposição diária (estoque único consolidado):
#   • Horizonte T (dias). Em cada dia t, existe DEMANDA[t] conhecida (derivada
#     da simulação) e um estoque atual s.
#   • DECISÃO q_t ∈ {0..Qmax}: quanto repor no começo do dia t.
#   • TRANSIÇÃO:  s' = max(0, s + q_t - DEMANDA[t])
#                 falta = max(0, DEMANDA[t] - (s + q_t))
#   • CUSTO INSTANTÂNEO:  C(q_t, s) = c*q_t + h*s' + p*falta
#       c = custo de compra/unidade (aprox. média do valor_unitario)
#       h = custo de estocagem/unidade remanescente ao fim do dia
#       p = penalidade por falta (quebra de atendimento)
#   • OBJETIVO: minimizar o custo total em T dias.
#   • ESTADO: (t, s) onde t ∈ {0..T} e s ∈ {0..Smax}.
#   • Função-valor V(t, s) = custo mínimo esperado do dia t ao final.
#       Bellman: V(t,s) = min_q [ C(q,s) + V(t+1, s') ].
#   • Condição de contorno: V(T, s) = 0 para todo s (horizonte finito).
# Observação: como a demanda é determinística (simulada), a PD é exata.
# =============================================================================

@dataclass
class DPParams:
    c: int = 1      # custo de compra por unidade
    h: int = 1      # custo de armazenagem por unidade (holding)
    p: int = 4      # custo de falta por unidade (penalidade)
    Qmax: int = 200 # máximo que posso comprar num dia
    Smax: int = 400 # capacidade (limite superior para discretização)

@dataclass
class DpResult:
    custo_total: int
    politica: List[int]  # tamanhos de pedido q_t
    trajetoria_estoque: List[int]

# -------- Top‑down com memoização ------------------------------------------------

def dp_topdown(demandas: List[int], S0: int, params: DPParams) -> DpResult:
    T = len(demandas)
    c, h, p, Qmax, Smax = params.c, params.h, params.p, params.Qmax, params.Smax

    @lru_cache(maxsize=None)
    def V(t: int, s: int) -> Tuple[int, int]:
        # retorna (custo_min, melhor_q)
        if t == T:
            return (0, 0)
        s = min(max(s, 0), Smax)
        best_cost = 10**12
        best_q = 0
        for q in range(0, Qmax+1):
            estoque_apos_compra = min(s + q, Smax)
            falta = max(0, demandas[t] - estoque_apos_compra)
            s_prime = max(0, estoque_apos_compra - demandas[t])
            custo_inst = c*q + h*s_prime + p*falta
            prox, _ = V(t+1, s_prime)
            total = custo_inst + prox
            if total < best_cost:
                best_cost, best_q = total, q
        return (best_cost, best_q)

    custo, _ = V(0, S0)
    # Reconstrução da política e trajetória
    polit, traj = [], [S0]
    s = S0
    for t in range(T):
        _, q = V(t, s)
        polit.append(q)
        estoque_apos_compra = min(s + q, Smax)
        s = max(0, estoque_apos_compra - demandas[t])
        traj.append(s)
    return DpResult(custo_total=custo, politica=polit, trajetoria_estoque=traj)

# -------- Bottom‑up -------------------------------------------------------------

def dp_bottomup(demandas: List[int], S0: int, params: DPParams) -> DpResult:
    T = len(demandas)
    c, h, p, Qmax, Smax = params.c, params.h, params.p, params.Qmax, params.Smax

    # T+1 x (Smax+1)
    V = [[0]*(Smax+1) for _ in range(T+1)]
    PI = [[0]*(Smax+1) for _ in range(T)]

    for t in range(T-1, -1, -1):
        d = demandas[t]
        for s in range(Smax+1):
            best, best_q = 10**12, 0
            for q in range(0, Qmax+1):
                estoque_apos_compra = min(s + q, Smax)
                falta = max(0, d - estoque_apos_compra)
                s_prime = max(0, estoque_apos_compra - d)
                total = c*q + h*s_prime + p*falta + V[t+1][s_prime]
                if total < best:
                    best, best_q = total, q
            V[t][s] = best
            PI[t][s] = best_q

    custo = V[0][min(S0, Smax)]
    polit, traj = [], [min(S0, Smax)]
    s = traj[0]
    for t in range(T):
        q = PI[t][s]
        polit.append(q)
        estoque_apos_compra = min(s + q, Smax)
        s = max(0, estoque_apos_compra - demandas[t])
        traj.append(s)
    return DpResult(custo_total=custo, politica=polit, trajetoria_estoque=traj)

# -------- Utilidades para preparar demandas a partir da simulação ---------------

def demandas_por_dia(registros: List[Consumo]) -> List[int]:
    if not registros: return []
    by_day: Dict[date, int] = {}
    for r in registros:
        by_day[r.data] = by_day.get(r.data, 0) + r.quantidade_consumida
    dias = sorted(by_day.keys())
    return [by_day[d] for d in dias]

# =============================================================================
# RELATÓRIO AMPLIADO
# =============================================================================
RELATORIO_PATH = "relatorio_dynamic_programming.txt"


def calcular_valores(estoque_snapshot: dict) -> str:
    out = ["=== VALOR ATUAL E IDEAL POR SETOR E PRODUTO ===\n"]
    for setor, itens in estoque_snapshot.items():
        valor_atual_setor = 0.0
        valor_ideal_setor = 0.0
        out.append(f"Setor: {setor}")
        for item, dados in itens.items():
            valor_atual = dados["quantidade"] * dados["valor_unitario"]
            valor_ideal = dados["ideal"] * dados["valor_unitario"]
            valor_atual_setor += valor_atual
            valor_ideal_setor += valor_ideal
            out.append(
                f"  Produto: {item}\n"
                f"    Quantidade atual: {dados['quantidade']} x R$ {dados['valor_unitario']:.2f} = R$ {valor_atual:.2f}\n"
                f"    Quantidade ideal: {dados['ideal']} x R$ {dados['valor_unitario']:.2f} = R$ {valor_ideal:.2f}\n"
            )
        out.append(f"  Valor total atual do setor: R$ {valor_atual_setor:.2f}")
        out.append(f"  Valor total ideal do setor: R$ {valor_ideal_setor:.2f}\n")
    return "\n".join(out)


def produtos_em_falta(estoque_snapshot: dict) -> str:
    out = ["=== PRODUTOS EM FALTA ===\n"]
    for setor, itens in estoque_snapshot.items():
        for item, dados in itens.items():
            if dados["quantidade"] < dados["ideal"]:
                falta = dados["ideal"] - dados["quantidade"]
                out.append(f"{item} no setor {setor}: falta {falta} unidades")
    return "\n".join(out)


def produtos_sobrando(estoque_snapshot: dict) -> str:
    out = ["=== PRODUTOS SOBRANDO ===\n"]
    for setor, itens in estoque_snapshot.items():
        for item, dados in itens.items():
            if dados["quantidade"] > dados["ideal"]:
                sobra = dados["quantidade"] - dados["ideal"]
                out.append(f"{item} no setor {setor}: sobrando {sobra} unidades")
    return "\n".join(out)


def gerar_relatorio(estoque_snapshot: dict, registros: List[Consumo],
                    dp_td: Optional[DpResult] = None,
                    dp_bu: Optional[DpResult] = None,
                    params: Optional[DPParams] = None) -> str:
    linhas = []
    linhas.append("# RELATÓRIO — Sprint 3 (Dynamic Programming)\n")

    linhas.append("## Objetivo\n")
    linhas.append(textwrap.dedent(
        """
        Organizar e consultar os dados de consumo com estruturas clássicas e
        modelar a reposição via Programação Dinâmica para reduzir faltas e
        desperdícios, garantindo visão de consumo e política ótima de compra.
        """
    ).strip()+"\n")

    linhas.append("\n## Estoque (snapshot após simulação)\n")
    linhas.append(calcular_valores(estoque_snapshot))
    linhas.append(produtos_em_falta(estoque_snapshot))
    linhas.append(produtos_sobrando(estoque_snapshot))

    if dp_td and dp_bu and params:
        iguais = (dp_td.custo_total == dp_bu.custo_total and dp_td.politica == dp_bu.politica)
        linhas.append("\n## Programação Dinâmica — Formulação\n")
        linhas.append(textwrap.dedent(
            f"""
            • Estado: (t, s) — dia t e estoque s.\n
            • Decisão: q_t em [0, {params.Qmax}] (unidades a repor no início do dia).\n
            • Transição: s' = max(0, s + q_t − demanda[t]).\n              Falta = max(0, demanda[t] − (s + q_t)).\n
            • Função objetivo: minimizar ∑(c*q_t + h*s' + p*Falta).\n              Parâmetros usados: c={params.c}, h={params.h}, p={params.p}.\n
            • Implementações: Recursiva com memoização (top‑down) e Iterativa (bottom‑up).\n              Ambas produziram o mesmo resultado? {"Sim" if iguais else "Não"}.\n            • Custo mínimo encontrado: {dp_td.custo_total}.\n            • Política ótima de pedidos (q_t): {dp_td.politica}.\n            • Trajetória de estoque: {dp_td.trajetoria_estoque}.
            """
        ).strip()+"\n")

    linhas.append("\n## Como executar\n")
    linhas.append(textwrap.dedent(
        """
        1. Execute `python sprint.py`.
        2. Pelo menu, use: (1) Simular, (2) Fila, (3) Pilha, (4) Buscar,
           (5) Ordenar, (6) Relatório, (7) Otimizar Reposição (PD).
        3. O relatório é salvo como `relatorio_dynamic_programming.txt`.
        """
    ).strip()+"\n")

    conteudo = "\n".join(linhas)
    with open(RELATORIO_PATH, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return os.path.abspath(RELATORIO_PATH)

# =============================================================================
# MENU / ORQUESTRAÇÃO
# =============================================================================

REGISTROS: List[Consumo] = []
DP_PARAMS = DPParams()  # pode ajustar no menu


def _menu():
    print("\n=== MENU SPRINT 3 — Dynamic Programming ===")
    print("1) Simular consumo (gera registros)")
    print("2) Ver Fila (FIFO)")
    print("3) Ver Pilha (LIFO)")
    print("4) Buscar item (Sequencial/Binária)")
    print("5) Ordenar (quantidade/validade)")
    print("6) Gerar Relatório")
    print("7) Otimizar Reposição (Programação Dinâmica)")
    print("8) Ajustar Parâmetros da PD (c,h,p,Qmax,Smax)")
    print("0) Sair")


def _pause():
    input("\nPressione <Enter> para continuar...")


if __name__ == "__main__":
    while True:
        _menu()
        op = input("> ").strip()

        if op == "1":
            try:
                dias = int(input("Quantos dias simular? [7]: ") or 7)
                seed = int(input("Semente aleatória? [42]: ") or 42)
            except ValueError:
                dias, seed = 7, 42
            REGISTROS = simular_consumo(estoque, dias=dias, semente=seed)
            print(f"Gerados {len(REGISTROS)} registros.")
            _pause()

        elif op == "2":
            if not REGISTROS: print("Simule primeiro."); _pause(); continue
            fila = FilaConsumo(); [fila.enfileirar(r) for r in REGISTROS]
            print("— Fila (10 primeiros) —")
            for r in fila.listar()[:10]: print(r)
            _pause()

        elif op == "3":
            if not REGISTROS: print("Simule primeiro."); _pause(); continue
            pilha = PilhaConsumo(); [pilha.empilhar(r) for r in REGISTROS]
            print("— Pilha (10 primeiros) —")
            for r in pilha.listar()[:10]: print(r)
            _pause()

        elif op == "4":
            if not REGISTROS: print("Simule primeiro."); _pause(); continue
            alvo = input("Item para buscar [Reagentes]: ") or "Reagentes"
            seq = [r for r in REGISTROS if r.item.lower()==alvo.lower()]
            regs_item = merge_sort(REGISTROS, key=lambda r: r.item.lower())
            # busca binária simples por fatia
            lo, hi = 0, len(regs_item)-1; pos=-1
            while lo<=hi:
                mid=(lo+hi)//2; m=regs_item[mid].item.lower()
                if m==alvo.lower(): pos=mid; break
                if m<alvo.lower(): lo=mid+1
                else: hi=mid-1
            bin_=[]
            if pos!=-1:
                i=pos
                while i>=0 and regs_item[i].item.lower()==alvo.lower(): bin_.append(regs_item[i]); i-=1
                j=pos+1
                while j<len(regs_item) and regs_item[j].item.lower()==alvo.lower(): bin_.append(regs_item[j]); j+=1
            print(f"Sequencial: {len(seq)} | Binária: {len(bin_)}")
            for r in seq[:5]: print(r)
            _pause()

        elif op == "5":
            if not REGISTROS: print("Simule primeiro."); _pause(); continue
            print("1) MergeSort por quantidade (asc)\n2) QuickSort por quantidade (desc)\n3) MergeSort por validade (asc)")
            s = input("> ").strip() or "1"
            if s=="1": ordenados = merge_sort(REGISTROS, key=lambda r: r.quantidade_consumida)
            elif s=="2": ordenados = list(reversed(quick_sort(REGISTROS, key=lambda r: r.quantidade_consumida)))
            else: ordenados = merge_sort(REGISTROS, key=lambda r: r.validade)
            for r in ordenados[:10]: print(r)
            _pause()

        elif op == "6":
            if not REGISTROS: print("Simule primeiro."); _pause(); continue
            # Se já houver resultado de PD, vamos computar aqui para cair no relatório
            dmd = demandas_por_dia(REGISTROS)
            S0 = sum(v["quantidade"] for setor in estoque.values() for v in setor.values())
            td = dp_topdown(dmd, S0=min(S0, DP_PARAMS.Smax), params=DP_PARAMS) if dmd else None
            bu = dp_bottomup(dmd, S0=min(S0, DP_PARAMS.Smax), params=DP_PARAMS) if dmd else None
            path = gerar_relatorio(estoque, REGISTROS, td, bu, DP_PARAMS)
            print(f"Relatório gerado em: {path}")
            _pause()

        elif op == "7":
            if not REGISTROS: print("Simule primeiro."); _pause(); continue
            dmd = demandas_por_dia(REGISTROS)
            if not dmd: print("Sem demandas."); _pause(); continue
            S0 = sum(v["quantidade"] for setor in estoque.values() for v in setor.values())
            S0 = min(S0, DP_PARAMS.Smax)
            td = dp_topdown(dmd, S0=S0, params=DP_PARAMS)
            bu = dp_bottomup(dmd, S0=S0, params=DP_PARAMS)
            print("— Programação Dinâmica —")
            print(f"Top‑down custo: {td.custo_total}\nPolítica: {td.politica}")
            print(f"Bottom‑up custo: {bu.custo_total}\nPolítica: {bu.politica}")
            iguais = (td.custo_total==bu.custo_total and td.politica==bu.politica)
            print("Equivalência (custo e política):", "OK" if iguais else "DIFERENTE")
            _pause()

        elif op == "8":
            try:
                c = int(input(f"custo unidade [atual {DP_PARAMS.c}]:") or DP_PARAMS.c)
                h = int(input(f"holding/unid [atual {DP_PARAMS.h}]:") or DP_PARAMS.h)
                p = int(input(f"penalidade falta [atual {DP_PARAMS.p}]:") or DP_PARAMS.p)
                Q = int(input(f"Qmax [atual {DP_PARAMS.Qmax}]:") or DP_PARAMS.Qmax)
                S = int(input(f"Smax [atual {DP_PARAMS.Smax}]:") or DP_PARAMS.Smax)
                DP_PARAMS = DPParams(c=c,h=h,p=p,Qmax=Q,Smax=S)  # type: ignore
                print("Parâmetros atualizados.")
            except Exception:
                print("Parâmetros mantidos.")
            _pause()

        elif op == "0":
            break
        else:
            print("Opção inválida.")
            _pause()
