"""
Algoritmos del Subproyecto 2: reparto de presupuesto y selección de participantes.

Parte 1 (reparto):    reparto_voraz      -> exacto, O(N + B log N)
Parte 2 (selección):  seleccion_exacta   -> exacto, C(N,k) evaluaciones de f
                      seleccion_voraz    -> aproximado (1 - 1/e), N*k evaluaciones de f

La utilidad de la Parte 2 es la de cobertura: f(A) = |unión de S[j] con j en A|.
"""
import heapq
import math


# =====================================================================
# PARTE 1: reparto voraz por ganancia marginal (Algoritmo 1 del informe)
# =====================================================================
def reparto_voraz(u, N, B):
    """u(i, x) = utilidad del nodo i si recibe x unidades (cóncava y creciente).
    Devuelve x[0..N-1] con sum(x) = B."""
    g = lambda i, x: u(i, x + 1) - u(i, x)        # ganancia marginal g_i(x)
    x = [0] * N                                   # línea 1
    H = [(-g(i, 0), i) for i in range(N)]         # líneas 2-3 (signo - => montículo de máximos)
    heapq.heapify(H)                              # línea 4, O(N)
    for _ in range(B):                            # línea 5
        _, i = heapq.heappop(H)                   # línea 6, O(log N)
        x[i] += 1                                 # línea 7
        heapq.heappush(H, (-g(i, x[i]), i))       # línea 8, O(log N)
    return x


def utilidad_log(w):
    """u_i(x) = w_i * ln(1 + x): creciente y cóncava, evaluable en O(1)."""
    return lambda i, x: w[i] * math.log1p(x)


def utilidad_total(u, x):
    return sum(u(i, xi) for i, xi in enumerate(x))


# =====================================================================
# PARTE 2: utilidad de cobertura
# =====================================================================
def f_cobertura(S, A):
    """f(A) = |unión de S[j], j en A|. Costo tau = O(sum_{j en A} |S[j]|)."""
    cubierto = set()
    for j in A:
        cubierto |= S[j]
    return len(cubierto)


# =====================================================================
# PARTE 2: selección exacta por fuerza bruta (Algoritmo 2 del informe)
# =====================================================================
def seleccion_exacta(S, k):
    """Recorre el árbol incluir / no incluir. Devuelve (v*, A*) y cuántas
    veces evaluó f (debe ser C(N, k))."""
    N = len(S)
    evaluaciones = [0]

    def exacto(i, A):
        if len(A) == k:                                   # caso 1: cupo lleno (hoja)
            evaluaciones[0] += 1
            return f_cobertura(S, A), list(A)
        quedan, faltan = N - i, k - len(A)                # i va de 0 a N-1 en Python
        if quedan < faltan:                               # caso 2: poda
            return -math.inf, []
        A.append(i)
        v1, A1 = exacto(i + 1, A)                         # caso 3a: incluir i
        A.pop()
        v2, A2 = exacto(i + 1, A)                         # caso 3b: no incluir i
        return (v1, A1) if v1 >= v2 else (v2, A2)

    v, A = exacto(0, [])
    return v, A, evaluaciones[0]


# =====================================================================
# PARTE 2: selección voraz (Algoritmo 3 del informe)
# =====================================================================
def seleccion_voraz(S, k):
    """Devuelve (f(A), A, evaluaciones). Cada evaluación de la ganancia
    marginal cuesta tau = O(|S[j]|) gracias al conjunto 'cubierto'."""
    N = len(S)
    A, en_A, cubierto = [], [False] * N, set()
    evaluaciones = 0
    for _ in range(k):                                    # una vuelta por lugar del cupo
        mejor, mejor_delta = -1, -1
        for j in range(N):
            if not en_A[j]:                               # los que ya están en el grupo se saltan
                delta = len(S[j] - cubierto)              # Delta_j(A) = |S_j \ C(A)|
                evaluaciones += 1
                if delta > mejor_delta:
                    mejor, mejor_delta = j, delta
        A.append(mejor)
        en_A[mejor] = True
        cubierto |= S[mejor]
    return len(cubierto), A, evaluaciones


if __name__ == "__main__":
    # Ejemplo del informe (Parte 1)
    u = utilidad_log([10, 8, 7])
    print("Reparto voraz:", reparto_voraz(u, N=3, B=5))
    # Ejemplo del informe (Parte 2)
    S = [{1, 2, 3}, {3, 4}, {4, 5, 6}, {1, 4}]
    print("Exacto:", seleccion_exacta(S, 2))
    print("Voraz :", seleccion_voraz(S, 2))
    # Instancia donde el voraz no es óptimo
    S = [{1, 2, 3, 4}, {1, 2, 5}, {3, 4, 6}]
    print("Exacto:", seleccion_exacta(S, 2), " Voraz:", seleccion_voraz(S, 2))
