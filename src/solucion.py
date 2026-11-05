"""
Solución base del Subproyecto 2 aplicada a un caso, con traza opcional.

  Parte 2  seleccion_voraz_traza : voraz por ganancia marginal (Algoritmo 3 del informe)
  Parte 1  reparto_voraz_traza   : voraz con montículo (Algoritmo 1 del informe)
  Apoyo    f_cobertura, seleccion_exacta_ref, resolver

La traza solo OBSERVA: con o sin ella, las decisiones son las mismas.
Desempate: siempre gana el nodo de menor índice (orden del archivo).

Utilidad conjunta (Parte 2): f(A) = |unión de S[j], j en A|, la cobertura de categorías del informe.
Utilidad individual (Parte 1): u_i(x) elegible (ver utilidades.py; por defecto w_i ln(1+x)),
con w_i = coeficiente_utilidad.
"""
import heapq
import itertools
import math

from utilidades import construir


def f_cobertura(S, A):
    """Utilidad conjunta f(A) = |unión de S[j], j en A|, calculada desde cero.

    Args:
        S: S[j] = conjunto de categorías del nodo j.
        A: iterable de índices de los nodos seleccionados (puede estar vacío).

    Returns:
        int, número de categorías distintas cubiertas.

    Complejidad: O(suma de |S[j]| para j en A) tiempo y memoria (es el costo tau del informe).
    """
    cubierto = set()
    for j in A:
        cubierto |= S[j]
    return len(cubierto)


def seleccion_voraz_traza(S, k, traza=None):
    """Selección voraz de k nodos por mayor ganancia marginal (Algoritmo 3 del informe).

    En cada una de las k iteraciones calcula, para cada nodo j fuera de A,
    Delta_j(A) = f(A + {j}) - f(A) = |S[j] \\ cubierto| (las categorías de j aún no cubiertas)
    y agrega el j de mayor Delta (en empate, el de menor índice porque la comparación es '>' estricta).
    Como f es monótona y submodular, f(A) >= (1 - 1/e) * f(óptimo).

    Args:
        S:     S[j] = conjunto de categorías del nodo j.
        k:     número de nodos a elegir (1 <= k < N).
        traza: lista opcional; si se da, se le agrega un dict por iteración con las claves
               iteracion, deltas ({nodo: Delta_j} de TODOS los candidatos), elegido, ganancia (su Delta),
               nuevas (categorías que aporta el elegido, ordenadas) y f_acumulada (f(A) tras agregarlo).
               No afecta a las decisiones.

    Returns:
        (A, f(A)): A es la lista de índices en el orden en que se eligieron.

    Complejidad: O(k * N * s) tiempo con s = máximo |S[j]| (k*N evaluaciones de Delta, cada una O(s));
    O(N + total de categorías) memoria extra (más O(k * N) si se pide traza).
    """
    N = len(S)
    A, en_A, cubierto = [], [False] * N, set()
    for it in range(1, k + 1):
        deltas = {}
        mejor, mejor_delta = None, -1
        for j in range(N):
            if en_A[j]:
                continue
            delta = len(S[j] - cubierto)      # Delta_j(A)
            deltas[j] = delta
            if delta > mejor_delta:           # '>' estricto: gana el menor índice en empates
                mejor, mejor_delta = j, delta
        nuevas = sorted(S[mejor] - cubierto)
        A.append(mejor)
        en_A[mejor] = True
        cubierto |= S[mejor]
        if traza is not None:
            traza.append(dict(iteracion=it, deltas=deltas, elegido=mejor, ganancia=mejor_delta,
                              nuevas=nuevas, f_acumulada=len(cubierto)))
    return A, len(cubierto)


def seleccion_exacta_ref(S, k, limite=2_000_000):
    """Óptimo exacto de la selección por fuerza bruta; sirve de referencia para medir al voraz.

    Prueba los C(N, k) subconjuntos y devuelve el de mayor f. Solo se ejecuta si C(N, k) <= limite,
    porque el problema es NP-difícil.

    Args:
        S:      S[j] = conjunto de categorías del nodo j.
        k:      tamaño del subconjunto.
        limite: máximo de combinaciones que se acepta evaluar.

    Returns:
        (f*, A*) con el mejor valor y un subconjunto que lo alcanza, o None si C(N, k) > limite.

    Complejidad: O(C(N, k) * k * s) tiempo; O(k) memoria.
    """
    if math.comb(len(S), k) > limite:
        return None
    return max(((f_cobertura(S, A), list(A)) for A in itertools.combinations(range(len(S)), k)),
               key=lambda t: t[0])


def reparto_voraz_traza(w, B, traza=None, spec=None):
    """Reparto exacto de B unidades enteras entre n nodos (Algoritmo 1 del informe).

    Entrega las unidades de una en una al nodo con mayor ganancia marginal g_i(x) = u_i(x+1) - u_i(x),
    usando un montículo de máximos. Es óptimo porque cada u_i es creciente y cóncava. Siempre reparte
    exactamente B unidades (gastar de más nunca perjudica porque u_i es creciente).

    Args:
        w:     w[i] = coeficiente_utilidad del i-ésimo nodo seleccionado (lista de longitud n).
        B:     unidades a repartir (entero >= 0).
        traza: lista opcional; se le agrega un dict por unidad con paso, nodo (posición en w),
               ganancia (g que tenía), x_nodo (unidades del nodo tras darle esta) y proxima_ganancia.
        spec:  función de utilidad, p. ej. {"tipo": "saturacion"}; None equivale a log.

    Returns:
        x: lista con x[i] unidades para el nodo i; sum(x) == B.

    Complejidad: O(n + B log n) tiempo (pseudo-polinomial en B), O(n) memoria.
    """
    u = construir(spec, w)
    g = lambda i, x: u(i, x + 1) - u(i, x)          # ganancia marginal g_i(x)
    n = len(w)
    x = [0] * n
    H = [(-g(i, 0), i) for i in range(n)]           # signo '-': heapq es de mínimos; (-g, i) desempata por i
    heapq.heapify(H)
    for paso in range(1, B + 1):
        neg, i = heapq.heappop(H)
        x[i] += 1
        sig = g(i, x[i])
        heapq.heappush(H, (-sig, i))
        if traza is not None:
            traza.append(dict(paso=paso, nodo=i, ganancia=-neg, x_nodo=x[i], proxima_ganancia=sig))
    return x


def resolver(caso, traza_sel=None, traza_rep=None):
    """Resuelve el caso completo: selecciona k nodos y reparte B entre ellos.

    Args:
        caso:      `Caso` validado (ver entrada.py).
        traza_sel: lista opcional para la traza de la selección.
        traza_rep: lista opcional para la traza del reparto.

    Returns:
        (A, fA, x): A = índices de los nodos elegidos, fA = f(A), x[i] = unidades de A[i].

    Complejidad: O(k N s + B log k).
    """
    A, fA = seleccion_voraz_traza(caso.S, caso.k, traza_sel)
    x = reparto_voraz_traza([caso.coef[j] for j in A], caso.B, traza_rep, caso.utilidad)
    return A, fA, x
