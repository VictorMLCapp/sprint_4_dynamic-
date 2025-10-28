# =============================================================================
# SISTEMA DE GESTÃO DE ESTOQUE HOSPITALAR — SPRINT 3 (Atualizado)
# =============================================================================
# Requisitos atendidos (conforme slide):
#   • Fila (FIFO) e Pilha (LIFO) .............................. 30 pts
#   • Estruturas de busca (Sequencial e Binária) .............. 20 pts
#   • Ordenação (Merge Sort e Quick Sort) ..................... 30 pts
#   • Relatório (código + explicação de uso) .................. 20 pts
# -----------------------------------------------------------------------------
# Este arquivo é autocontido: ao executar, você pode usar um menu simples
# para simular consumos, consultar fila/pilha, buscar e ordenar registros,
# e gerar um relatório (.txt) pronto para subir no GitHub.
# =============================================================================

from collections import deque
from dataclasses import dataclass
from datetime import date, timedelta
from typing import List, Callable, Any, Optional
import random
import textwrap
import os

# =============================================================================
# DADOS INICIAIS DO ESTOQUE HOSPITALAR
# =============================================================================
estoque = {
    "Triagem": {
        "Luvas": {"quantidade": 250, "ideal": 200, "valor_unitario": 0.50, "validade": "2025-12-20"},
        "Seringas": {"quantidade": 80, "ideal": 100, "valor_unitario": 1.00, "validade": "2025-11-05"}
    },
    "Laboratório": {
        "Tubos de ensaio": {"quantidade": 60, "ideal": 100, "valor_unitario": 2.00, "validade": "2026-01-10"},
        "Reagentes": {"quantidade": 50, "ideal": 70, "valor_unitario": 5.00, "validade": "2025-10-25"}
    },
    "Recepção": {
        "Máscaras": {"quantidade": 170, "ideal": 150, "valor_unitario": 0.75, "validade": "2026-03-01"}
    }
}

# =============================================================================
# UTILITÁRIOS
# =============================================================================

def str_to_date(yyyy_mm_dd: str) -> date:
    y, m, d = map(int, yyyy_mm_dd.split("-"))
    return date(y, m, d)

# =============================================================================
# ENTIDADES E ESTRUTURAS
# =============================================================================

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
# FUNÇÕES DE ANÁLISE
# =============================================================================

def calcular_valores(estoque: dict) -> str:
    out = ["=== VALOR ATUAL E IDEAL POR SETOR E PRODUTO ===\n"]
    for setor, itens in estoque.items():
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

def produtos_em_falta(estoque: dict) -> str:
    out = ["=== PRODUTOS EM FALTA ===\n"]
    for setor, itens in estoque.items():
        for item, dados in itens.items():
            if dados["quantidade"] < dados["ideal"]:
                falta = dados["ideal"] - dados["quantidade"]
                out.append(f"{item} no setor {setor}: falta {falta} unidades")
    return "\n".join(out)

def produtos_sobrando(estoque: dict) -> str:
    out = ["=== PRODUTOS SOBRANDO ===\n"]
    for setor, itens in estoque.items():
        for item, dados in itens.items():
            if dados["quantidade"] > dados["ideal"]:
                sobra = dados["quantidade"] - dados["ideal"]
                out.append(f"{item} no setor {setor}: sobrando {sobra} unidades")
    return "\n".join(out)

# =============================================================================
# SIMULAÇÃO
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
                consumido = min(consumido, dados["quantidade"])  # não passar do estoque
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
# BUSCAS
# =============================================================================

def busca_sequencial(registros: List[Consumo], nome_item: str) -> List[Consumo]:
    alvo = nome_item.lower()
    return [r for r in registros if r.item.lower() == alvo]


def busca_binaria_por_item(registros_ordenados_por_item: List[Consumo], nome_item: str) -> List[Consumo]:
    alvo = nome_item.lower()
    lo, hi = 0, len(registros_ordenados_por_item) - 1
    pos = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        meio = registros_ordenados_por_item[mid].item.lower()
        if meio == alvo:
            pos = mid
            break
        if meio < alvo:
            lo = mid + 1
        else:
            hi = mid - 1
    if pos == -1:
        return []
    # coleta ocorrências vizinhas
    out = [registros_ordenados_por_item[pos]]
    i = pos - 1
    while i >= 0 and registros_ordenados_por_item[i].item.lower() == alvo:
        out.append(registros_ordenados_por_item[i])
        i -= 1
    j = pos + 1
    while j < len(registros_ordenados_por_item) and registros_ordenados_por_item[j].item.lower() == alvo:
        out.append(registros_ordenados_por_item[j])
        j += 1
    return sorted(out, key=lambda r: (r.data, r.setor))

# =============================================================================
# ORDENAÇÃO (MERGE SORT e QUICK SORT)
# =============================================================================

def merge_sort(arr: List[Any], key: Callable[[Any], Any]) -> List[Any]:
    if len(arr) <= 1:
        return arr[:]
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key)
    right = merge_sort(arr[mid:], key)
    return _merge(left, right, key)


def _merge(left: List[Any], right: List[Any], key: Callable[[Any], Any]) -> List[Any]:
    i = j = 0
    out: List[Any] = []
    while i < len(left) and j < len(right):
        if key(left[i]) <= key(right[j]):
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


def quick_sort(arr: List[Any], key: Callable[[Any], Any]) -> List[Any]:
    if len(arr) <= 1:
        return arr[:]
    pivot = key(arr[len(arr)//2])
    menores = [x for x in arr if key(x) < pivot]
    iguais  = [x for x in arr if key(x) == pivot]
    maiores = [x for x in arr if key(x) > pivot]
    return quick_sort(menores, key) + iguais + quick_sort(maiores, key)

# =============================================================================
# RELATÓRIO
# =============================================================================

RELATORIO_PATH = "relatorio_dynamic_programming.txt"

def gerar_relatorio(estoque_snapshot: dict, registros: List[Consumo]) -> str:
    """Gera um relatório de uso das estruturas/algoritmos e salva em .txt."""
    linhas = []
    linhas.append("# RELATÓRIO — Sprint 3 (Dynamic Programming)\n")
    linhas.append("## Objetivo\n")
    linhas.append(textwrap.dedent(
        """
        Organizar e consultar os dados de consumo diário de insumos utilizando
        estruturas de dados clássicas (Fila e Pilha), buscas (Sequencial e
        Binária) e algoritmos de ordenação (Merge Sort e Quick Sort).
        """
    ).strip()+"\n")

    linhas.append("\n## Estoque (snapshot após simulação)\n")
    linhas.append(calcular_valores(estoque_snapshot))
    linhas.append(produtos_em_falta(estoque_snapshot))
    linhas.append(produtos_sobrando(estoque_snapshot))

    linhas.append("\n## Estruturas de Dados\n")
    linhas.append(textwrap.dedent(
        """
        • Fila (FIFO): registra os consumos em ordem cronológica de ocorrência.
        • Pilha (LIFO): permite consultar primeiro os consumos mais recentes.
        """
    ).strip()+"\n")

    # Pré-visualização de 5 registros em cada estrutura
    fila = FilaConsumo(); [fila.enfileirar(r) for r in registros]
    pilha = PilhaConsumo(); [pilha.empilhar(r) for r in registros]
    linhas.append("Exemplos na Fila (5):\n" + "\n".join(map(str, fila.listar()[:5])) + "\n")
    linhas.append("Exemplos na Pilha (5):\n" + "\n".join(map(str, pilha.listar()[:5])) + "\n")

    linhas.append("\n## Buscas\n")
    target = "Reagentes"
    seq = busca_sequencial(registros, target)
    regs_item = merge_sort(registros, key=lambda r: r.item.lower())
    bin_ = busca_binaria_por_item(regs_item, target)
    linhas.append(f"Sequencial por '{target}': {len(seq)} achados\n")
    linhas.append(f"Binária por '{target}': {len(bin_)} achados\n")

    linhas.append("\n## Ordenações\n")
    linhas.append("Merge Sort por quantidade (asc, 5):\n" + "\n".join(map(str, merge_sort(registros, key=lambda r: r.quantidade_consumida)[:5])) + "\n")
    qs = quick_sort(registros, key=lambda r: r.quantidade_consumida)
    linhas.append("Quick Sort por quantidade (desc, 5):\n" + "\n".join(map(str, list(reversed(qs))[:5])) + "\n")
    linhas.append("Por validade (mais próximos do vencimento, 5):\n" + "\n".join(map(str, merge_sort(registros, key=lambda r: r.validade)[:5])) + "\n")

    linhas.append("\n## Como executar\n")
    linhas.append(textwrap.dedent(
        """
        1. Execute `python sprint.py`.
        2. Pelo menu, escolha: (1) Simular, (2) Fila, (3) Pilha, (4) Buscar,
           (5) Ordenar, (6) Relatório, (0) Sair.
        3. O relatório é salvo como `relatorio_dynamic_programming.txt` na raiz.
        """
    ).strip()+"\n")

    conteudo = "\n".join(linhas)
    with open(RELATORIO_PATH, "w", encoding="utf-8") as f:
        f.write(conteudo)
    return os.path.abspath(RELATORIO_PATH)

# =============================================================================
# MENU INTERATIVO (opcional para correção)
# =============================================================================

def _menu():
    print("\n=== MENU SPRINT 3 — Dynamic Programming ===")
    print("1) Simular consumo (gera registros)")
    print("2) Ver Fila (FIFO)")
    print("3) Ver Pilha (LIFO)")
    print("4) Buscar item (sequencial e binária)")
    print("5) Ordenar (quantidade/validade)")
    print("6) Gerar Relatório")
    print("0) Sair")


def _pause():
    input("\nPressione <Enter> para continuar...")


# Estado compartilhado da execução
REGISTROS: List[Consumo] = []

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
            print(f"Foram gerados {len(REGISTROS)} registros de consumo.")
            _pause()

        elif op == "2":  # Fila
            if not REGISTROS:
                print("Nenhum registro. Use a opção 1 para simular."); _pause(); continue
            fila = FilaConsumo(); [fila.enfileirar(r) for r in REGISTROS]
            print("\n— Primeiros 10 na Fila (cronológico) —")
            for r in fila.listar()[:10]:
                print(r)
            _pause()

        elif op == "3":  # Pilha
            if not REGISTROS:
                print("Nenhum registro. Use a opção 1 para simular."); _pause(); continue
            pilha = PilhaConsumo(); [pilha.empilhar(r) for r in REGISTROS]
            print("\n— Primeiros 10 na Pilha (recentes primeiro) —")
            for r in pilha.listar()[:10]:
                print(r)
            _pause()

        elif op == "4":  # Buscas
            if not REGISTROS:
                print("Nenhum registro. Use a opção 1 para simular."); _pause(); continue
            alvo = input("Item para buscar (ex.: Reagentes): ") or "Reagentes"
            seq = busca_sequencial(REGISTROS, alvo)
            regs_item = merge_sort(REGISTROS, key=lambda r: r.item.lower())
            bin_ = busca_binaria_por_item(regs_item, alvo)
            print(f"Sequencial por '{alvo}': {len(seq)} achados (mostrando até 5)")
            for r in seq[:5]: print(r)
            print(f"\nBinária por '{alvo}': {len(bin_)} achados (mostrando até 5)")
            for r in bin_[:5]: print(r)
            _pause()

        elif op == "5":  # Ordenações
            if not REGISTROS:
                print("Nenhum registro. Use a opção 1 para simular."); _pause(); continue
            print("\n1) MergeSort por quantidade (asc)\n2) QuickSort por quantidade (desc)\n3) MergeSort por validade (mais próximos primeiro)")
            s = input("> ").strip() or "1"
            if s == "1":
                ordenados = merge_sort(REGISTROS, key=lambda r: r.quantidade_consumida)
            elif s == "2":
                ordenados = list(reversed(quick_sort(REGISTROS, key=lambda r: r.quantidade_consumida)))
            else:
                ordenados = merge_sort(REGISTROS, key=lambda r: r.validade)
            for r in ordenados[:10]:
                print(r)
            _pause()

        elif op == "6":  # Relatório
            if not REGISTROS:
                print("Nenhum registro. Use a opção 1 para simular."); _pause(); continue
            path = gerar_relatorio(estoque, REGISTROS)
            print(f"Relatório gerado em: {path}")
            _pause()

        elif op == "0":
            break
        else:
            print("Opção inválida.")
            _pause()
