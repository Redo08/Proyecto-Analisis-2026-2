"""Verificación de restricciones de una ronda. Cada chequeo: nombre, esperado, obtenido, cumple, tipo.

tipo 'obligatoria' = restricción del problema base; 'informativa' = restricción del enunciado que la
solución base NO impone (variante pendiente en el informe) y que solo se reporta.
"""
import math

from solucion import f_total
from utilidades import construir

EPS = 1e-9


def _chk(nombre, esperado, obtenido, cumple, tipo="obligatoria"):
    return dict(nombre=nombre, esperado=esperado, obtenido=obtenido, cumple=bool(cumple), tipo=tipo)


def _no_crece(v):
    return all(v[i] >= v[i + 1] - EPS for i in range(len(v) - 1))


def verificar_ronda(caso, A, fA, x, tr_sel, tr_rep, ref, acumulado_antes):
    u = construir(caso.utilidad, [caso.coef[j] for j in A])
    cs = []
    validos = len(set(A)) == len(A) and all(0 <= j < caso.N for j in A)
    cs.append(_chk("|A| = k", caso.k, len(A), len(A) == caso.k))
    cs.append(_chk("nodos de A distintos y válidos", True, validos, validos))
    f_re = f_total(caso.P, A)
    cs.append(_chk("f(A) de la traza = f(A) recalculada desde cero", round(f_re, 9), round(fA, 9),
                   abs(f_re - fA) < EPS))
    ok = _no_crece([t["ganancia"] for t in tr_sel])
    cs.append(_chk("ganancias marginales de la selección no crecientes (submodularidad)", True, ok, ok))
    cs.append(_chk("sum(x) = B", caso.B, sum(x), sum(x) == caso.B))
    enteros = all(isinstance(v, int) and v >= 0 for v in x)
    cs.append(_chk("x_i entero >= 0", True, enteros, enteros))
    ok = _no_crece([t["ganancia"] for t in tr_rep])
    cs.append(_chk("ganancias del reparto no crecientes (concavidad)", True, ok, ok))
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
        cs.append(_chk("garantía f(voraz) >= (1-1/e) f(óptimo)", f">= {cota:.4f}", f"{fA:.4f}",
                       fA >= cota - EPS))
    costo = sum(caso.costo[j] for j in A)
    cs.append(_chk("costo de participación de A <= presupuesto de costos (la base no lo impone)",
                   f"<= {caso.B_costos}", costo, costo <= caso.B_costos, "informativa"))
    excede = [caso.ids[A[i]] for i in range(len(A))
              if acumulado_antes[A[i]] + x[i] > caso.pres_nodo[A[i]]]
    cs.append(_chk("consumo acumulado por nodo <= presupuesto_total_nodo (la base no lo impone)",
                   "sin excesos", "sin excesos" if not excede else "excede: " + ", ".join(excede),
                   not excede, "informativa"))
    return cs
