"""
Verificación de restricciones del resultado de un caso.

Cada chequeo es un dict con: nombre, esperado, obtenido y cumple (bool). Si alguno falla, la
ejecución termina con código de salida 1.
"""
import math
import os
import sys

from solucion import f_cobertura
from utilidades import construir

# Implementación de referencia del informe, para contrastar los resultados.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "Informe", "code"))
import algoritmos  # noqa: E402

EPS = 1e-9   # tolerancia para comparar números de punto flotante


def _chk(nombre, esperado, obtenido, cumple):
    """Arma un chequeo (ver el formato en la cabecera del módulo)."""
    return dict(nombre=nombre, esperado=esperado, obtenido=obtenido, cumple=bool(cumple))


def _no_crece(v):
    """True si la secuencia `v` es no creciente (con tolerancia EPS)."""
    return all(v[i] >= v[i + 1] - EPS for i in range(len(v) - 1))


def verificar(caso, A, fA, x, tr_sel, tr_rep, ref):
    """Comprueba que el resultado cumple las restricciones del problema.

    Chequeos:
      - tamaño de A = k, nodos distintos y válidos.
      - f(A) acumulada en la traza = f(A) recalculada desde cero.
      - Ganancias de la selección no crecientes (consecuencia de la submodularidad).
      - Selección idéntica a la de Informe/code/algoritmos.py (implementación del informe).
      - sum(x) = B y cada x_i entero >= 0.
      - Ganancias del reparto no crecientes (concavidad observada).
      - Reparto idéntico al de Informe/code/algoritmos.py.
      - Optimalidad del reparto: mover una unidad de un nodo a otro nunca mejora la utilidad
        (para u_i cóncavas, equivale a ser un óptimo global).
      - Garantía f(A) >= (1 - 1/e) * f(óptimo), solo si se calculó el óptimo exacto.

    Args:
        caso:           `Caso` (ver entrada.py).
        A:              índices de los nodos elegidos.
        fA:             f(A) devuelta por la selección.
        x:              x[i] = unidades que recibió A[i].
        tr_sel, tr_rep: trazas de la selección y del reparto.
        ref:            (f*, A*) del óptimo exacto, o None si no se calculó.

    Returns:
        Lista de chequeos (dicts).

    Complejidad: O(k N s + k^2 + B log k), dominada por repetir los algoritmos de referencia.
    """
    w = [caso.coef[j] for j in A]
    u = construir(caso.utilidad, w)
    cs = []
    validos = len(set(A)) == len(A) and all(0 <= j < caso.N for j in A)
    cs.append(_chk("tamaño de A = k", caso.k, len(A), len(A) == caso.k))
    cs.append(_chk("nodos de A distintos y válidos", True, validos, validos))
    f_re = f_cobertura(caso.S, A)
    cs.append(_chk("f(A) de la traza = f(A) recalculada desde cero", f_re, fA, f_re == fA))
    ok = _no_crece([t["ganancia"] for t in tr_sel])
    cs.append(_chk("ganancias marginales de la selección no crecientes (submodularidad)", True, ok, ok))
    _, A_inf, _ = algoritmos.seleccion_voraz(caso.S, caso.k)
    cs.append(_chk("selección idéntica a la implementación del informe (algoritmos.py)", A_inf, A, A_inf == A))
    cs.append(_chk("sum(x) = B", caso.B, sum(x), sum(x) == caso.B))
    enteros = all(isinstance(v, int) and v >= 0 for v in x)
    cs.append(_chk("x_i entero >= 0", True, enteros, enteros))
    ok = _no_crece([t["ganancia"] for t in tr_rep])
    cs.append(_chk("ganancias del reparto no crecientes (concavidad)", True, ok, ok))
    x_inf = algoritmos.reparto_voraz(u, len(A), caso.B)
    cs.append(_chk("reparto idéntico a la implementación del informe (algoritmos.py)", x_inf, x, x_inf == x))
    # optimalidad: mover una unidad de i a j nunca mejora
    mejora = 0.0
    for i in range(len(x)):
        for j in range(len(x)):
            if i != j and x[i] > 0:
                mejora = max(mejora, (u(i, x[i] - 1) - u(i, x[i])) + (u(j, x[j] + 1) - u(j, x[j])))
    cs.append(_chk("reparto óptimo: ninguna transferencia de 1 unidad mejora la utilidad", "<= 0",
                   f"{mejora:.3e}", mejora <= EPS))
    if ref is not None:
        cota = (1 - 1 / math.e) * ref[0]
        cs.append(_chk("garantía f(voraz) >= (1-1/e) f(óptimo)", f">= {cota:.4f}", fA, fA >= cota - EPS))
    return cs
