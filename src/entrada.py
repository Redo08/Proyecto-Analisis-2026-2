"""
Lectura y validación de un caso (archivo JSON).

Convierte el archivo de entrada en un objeto `Caso` listo para los algoritmos y rechaza, con un
mensaje que nombra el caso, cualquier dato inválido. El formato completo está en
docs/manual_tecnico.md §4. Las claves que este módulo no conoce se ignoran (así, un caso con campos
de variantes no soportadas, como grafo de influencia, costos de participación o rondas, se ejecuta
igual con la solución base).
"""
import json
import os
from dataclasses import dataclass

from utilidades import validar


@dataclass
class Caso:
    """Un caso de prueba ya validado. Los nodos se identifican por su posición 0..N-1 en el archivo.

    Atributos:
        nombre:    nombre del archivo sin extensión (identifica el caso en resultados/).
        N:         número de nodos.
        k:         cupo de participantes (1 <= k < N).
        B:         presupuesto de ruido, en unidades enteras (>= 0).
        ids:       ids de los nodos ("N01", ...) en el orden del archivo; ids[i] es el nodo i.
        coef:      coef[i] = coeficiente_utilidad (w_i > 0) del nodo i.
        S:         S[i] = conjunto (set) de categorías de datos del nodo i; f(A) = |unión de S[j]|.
        utilidad:  especificación de u_i(x), p. ej. {"tipo": "log"} (ver utilidades.py).
    """
    nombre: str
    N: int
    k: int
    B: int
    ids: list
    coef: list
    S: list
    utilidad: dict


def _exigir(cond, msg):
    """Lanza ValueError(msg) si `cond` es falsa. Evita repetir if/raise en las validaciones."""
    if not cond:
        raise ValueError(msg)


def cargar(ruta, utilidad=None):
    """Lee `ruta` (JSON), valida todos los campos y devuelve un `Caso`.

    Args:
        ruta:     camino del archivo .json.
        utilidad: especificación de u_i(x) que, si no es None, tiene prioridad sobre la clave
                  "funcion_utilidad" del archivo (así lo usa la opción --utilidad de la CLI).

    Returns:
        Caso con las categorías de cada nodo convertidas a conjuntos.

    Raises:
        ValueError: faltan claves obligatorias (si faltan las categorías, el mensaje indica cómo
            generarlas), numero_nodos no coincide con len(nodos), ids repetidos, k fuera de
            1 <= k < N, B no entero o negativo, coeficiente <= 0, categorías vacías o función de
            utilidad inválida.
        OSError / json.JSONDecodeError: el archivo no existe o no es JSON válido.

    Complejidad: O(N + total de categorías).
    """
    with open(ruta, encoding="utf-8") as fh:
        d = json.load(fh)
    nombre = os.path.splitext(os.path.basename(ruta))[0]
    for clave in ("parametros", "nodos"):
        _exigir(clave in d, f"{nombre}: falta la clave '{clave}'")
    p = d["parametros"]
    for clave in ("numero_nodos", "cupo_participantes_por_ronda_k", "presupuesto_ruido_por_ronda_B"):
        _exigir(clave in p, f"{nombre}: falta parametros.{clave}")

    nodos = d["nodos"]
    N = len(nodos)
    _exigir(p["numero_nodos"] == N, f"{nombre}: numero_nodos={p['numero_nodos']} pero hay {N} nodos")
    ids = [n["id"] for n in nodos]
    _exigir(len(set(ids)) == N, f"{nombre}: ids de nodos repetidos")
    k, B = p["cupo_participantes_por_ronda_k"], p["presupuesto_ruido_por_ronda_B"]
    _exigir(isinstance(k, int) and 1 <= k < N, f"{nombre}: se exige 1 <= k < N (k={k}, N={N})")
    _exigir(isinstance(B, int) and B >= 0, f"{nombre}: B debe ser un entero >= 0 (B={B})")
    coef = [n["coeficiente_utilidad"] for n in nodos]
    _exigir(all(c > 0 for c in coef), f"{nombre}: todo coeficiente_utilidad debe ser > 0")

    sin_cat = [n["id"] for n in nodos if "categorias" not in n]
    _exigir(not sin_cat, f"{nombre}: faltan 'categorias' en los nodos {sin_cat[:5]}. "
                         "Se pueden generar con: python src/generar_categorias.py <caso.json> -o <salida.json>")
    S = [set(n["categorias"]) for n in nodos]
    vacios = [ids[i] for i, s in enumerate(S) if not s]
    _exigir(not vacios, f"{nombre}: nodos con 'categorias' vacías: {vacios[:5]}")

    try:
        spec = validar(utilidad or d.get("funcion_utilidad"))
    except ValueError as e:
        raise ValueError(f"{nombre}: {e}") from None

    return Caso(nombre, N, k, B, ids, coef, S, spec)
