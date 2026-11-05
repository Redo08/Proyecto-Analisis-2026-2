"""Lectura y validación de un caso (archivo JSON). Formato documentado en docs/manual_tecnico.md §4."""
import json
import os
from dataclasses import dataclass

from utilidades import validar


@dataclass
class Caso:
    nombre: str
    N: int
    rondas: int
    k: int                  # cupo de participantes por ronda
    B: int                  # presupuesto de ruido por ronda
    B_costos: float         # presupuesto de costos de participación por ronda
    ids: list               # ids de nodos, en el orden del archivo
    coef: list              # coeficiente_utilidad w_i
    pres_nodo: list         # presupuesto_total_nodo
    costo: list             # costo_participacion
    utilidad: dict          # {"tipo": ..., ...} ver utilidades.py
    P: list                 # P[j][v] = influencia de j sobre v (matriz simétrica, diagonal = 1)


def _exigir(cond, msg):
    if not cond:
        raise ValueError(msg)


def cargar(ruta, utilidad=None):
    """utilidad: si no es None, reemplaza a "funcion_utilidad" del archivo."""
    with open(ruta, encoding="utf-8") as fh:
        d = json.load(fh)
    nombre = os.path.splitext(os.path.basename(ruta))[0]
    for clave in ("parametros", "grafo", "nodos"):
        _exigir(clave in d, f"{nombre}: falta la clave '{clave}'")
    p = d["parametros"]
    for clave in ("numero_nodos", "numero_rondas", "cupo_participantes_por_ronda_k",
                  "presupuesto_ruido_por_ronda_B"):
        _exigir(clave in p, f"{nombre}: falta parametros.{clave}")

    nodos = d["nodos"]
    N = len(nodos)
    _exigir(p["numero_nodos"] == N, f"{nombre}: numero_nodos={p['numero_nodos']} pero hay {N} nodos")
    ids = [n["id"] for n in nodos]
    _exigir(len(set(ids)) == N, f"{nombre}: ids de nodos repetidos")
    k, B, R = p["cupo_participantes_por_ronda_k"], p["presupuesto_ruido_por_ronda_B"], p["numero_rondas"]
    _exigir(isinstance(k, int) and 1 <= k < N, f"{nombre}: se exige 1 <= k < N (k={k}, N={N})")
    _exigir(isinstance(B, int) and B >= 0, f"{nombre}: B debe ser un entero >= 0 (B={B})")
    _exigir(isinstance(R, int) and R >= 1, f"{nombre}: numero_rondas debe ser un entero >= 1")
    coef = [n["coeficiente_utilidad"] for n in nodos]
    _exigir(all(c > 0 for c in coef), f"{nombre}: todo coeficiente_utilidad debe ser > 0")

    pos = {i: idx for idx, i in enumerate(ids)}
    P = [[1.0 if a == b else 0.0 for b in range(N)] for a in range(N)]
    for e in d["grafo"]:
        for extremo in (e["u"], e["v"]):
            _exigir(extremo in pos, f"{nombre}: la arista {e} usa un nodo inexistente")
        a, b, w = pos[e["u"]], pos[e["v"]], e["peso_influencia"]
        _exigir(a != b, f"{nombre}: arista con lazo {e}")
        _exigir(0 <= w <= 1, f"{nombre}: peso_influencia fuera de [0,1] en {e}")
        P[a][b] = P[b][a] = float(w)   # grafo no dirigido

    try:
        spec = validar(utilidad or d.get("funcion_utilidad"))
    except ValueError as e:
        raise ValueError(f"{nombre}: {e}") from None

    return Caso(nombre, N, R, k, B,
                p.get("presupuesto_costos_participacion_por_ronda", float("inf")),
                ids, coef,
                [n.get("presupuesto_total_nodo", float("inf")) for n in nodos],
                [n.get("costo_participacion", 0) for n in nodos], spec, P)
