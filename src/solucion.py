"""
Solución base del Subproyecto 2 aplicada a un caso (grafo + nodos), con traza opcional.

  Parte 2  seleccion_voraz_traza : voraz por ganancia marginal (Algoritmo 3 del informe)
  Parte 1  reparto_voraz_traza   : voraz con montículo (Algoritmo 1 del informe)

La traza solo OBSERVA: con o sin ella, las decisiones son las mismas.
Desempate: siempre gana el nodo de menor índice (orden del archivo).

Utilidad conjunta (Parte 2):  f(A) = sum_v max_{j en A} P[j][v]   (P[v][v] = 1)
es la cobertura ponderada por influencia; con pesos 0/1 es la cobertura |unión S_j| del informe.
Utilidad individual (Parte 1): u_i(x) elegible (ver utilidades.py; por defecto w_i ln(1+x)),
con w_i = coeficiente_utilidad.
"""
import heapq
import itertools
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Informe", "code"))
from utilidades import construir  # noqa: E402


def f_total(P, A):
    """f(A) calculada desde cero."""
    return sum(max(P[j][v] for j in A) for v in range(len(P))) if A else 0.0


def seleccion_voraz_traza(P, k, traza=None):
    """Devuelve (A, f(A)). Si traza es una lista, agrega un dict por iteración."""
    N = len(P)
    A, mejor_cob = [], [0.0] * N          # mejor_cob[v] = max_{j en A} P[j][v]
    for it in range(1, k + 1):
        deltas = {}
        mejor, mejor_delta = None, -1.0
        for j in range(N):
            if j in A:
                continue
            delta = sum(max(0.0, P[j][v] - mejor_cob[v]) for v in range(N))   # Delta_j(A)
            deltas[j] = delta
            if delta > mejor_delta:       # '>' estricto: gana el menor índice en empates
                mejor, mejor_delta = j, delta
        A.append(mejor)
        mejor_cob = [max(mejor_cob[v], P[mejor][v]) for v in range(N)]
        if traza is not None:
            traza.append(dict(iteracion=it, deltas=deltas, elegido=mejor,
                              ganancia=mejor_delta, f_acumulada=sum(mejor_cob)))
    return A, sum(mejor_cob)


def seleccion_exacta_ref(P, k, limite=2_000_000):
    """Referencia por fuerza bruta (solo si C(N,k) <= limite). Devuelve (f*, A*) o None."""
    if math.comb(len(P), k) > limite:
        return None
    return max(((f_total(P, A), list(A)) for A in itertools.combinations(range(len(P)), k)),
               key=lambda t: t[0])


def reparto_voraz_traza(w, B, traza=None, spec=None):
    """w[i] = coeficiente del i-ésimo nodo seleccionado; spec = función de utilidad
    (por defecto log). Devuelve x con sum(x) = B."""
    u = construir(spec, w)
    g = lambda i, x: u(i, x + 1) - u(i, x)          # ganancia marginal g_i(x)
    n = len(w)
    x = [0] * n
    H = [(-g(i, 0), i) for i in range(n)]
    heapq.heapify(H)
    for paso in range(1, B + 1):
        neg, i = heapq.heappop(H)
        x[i] += 1
        sig = g(i, x[i])
        heapq.heappush(H, (-sig, i))
        if traza is not None:
            traza.append(dict(paso=paso, nodo=i, ganancia=-neg, x_nodo=x[i], proxima_ganancia=sig))
    return x


def resolver_ronda(caso, traza_sel=None, traza_rep=None):
    """Una ronda completa: selecciona k nodos y reparte B. Devuelve (A, fA, x)."""
    A, fA = seleccion_voraz_traza(caso.P, caso.k, traza_sel)
    x = reparto_voraz_traza([caso.coef[j] for j in A], caso.B, traza_rep, caso.utilidad)
    return A, fA, x
