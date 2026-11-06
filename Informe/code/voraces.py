import heapq

# ---------------- PARTE 1: reparto del presupuesto ----------------
def reparto_voraz(ganancias, B):
    """ganancias[i][x] = lo que aporta la unidad x+1 al nodo i (decreciente)."""
    N = len(ganancias)
    x = [0] * N                                   # unidades de cada nodo
    # montículo de máximos (heapq es de mínimos, por eso el signo -)
    H = [(-ganancias[i][0], i) for i in range(N)]
    heapq.heapify(H)                              # O(N)
    for _ in range(B):                            # B pasos
        g, i = heapq.heappop(H)                   # nodo con mayor ganancia, O(log N)
        x[i] += 1                                 # le doy una unidad
        if x[i] < len(ganancias[i]):
            heapq.heappush(H, (-ganancias[i][x[i]], i))   # su siguiente ganancia
    return x

# ---------- PARTE 1 (versión real): las ganancias se calculan desde u_i ----------
def reparto_voraz_u(u, N, B):
    """u(i, x) = utilidad del nodo i si recibe x unidades (cóncava y creciente)."""
    g = lambda i, x: u(i, x + 1) - u(i, x)        # ganancia marginal, O(1)
    x = [0] * N
    H = [(-g(i, 0), i) for i in range(N)]         # solo N ganancias al inicio
    heapq.heapify(H)                              # O(N)
    for _ in range(B):                            # B pasos
        _, i = heapq.heappop(H)                   # O(log N)
        x[i] += 1
        heapq.heappush(H, (-g(i, x[i]), i))       # calcula SOLO la siguiente ganancia de i
    return x

# ---------------- PARTE 2: selección de participantes ----------------
def seleccion_voraz(S, k):
    """S[j] = conjunto de categorías del nodo j. f(A) = |unión de S[j], j en A|."""
    A, cubierto = [], set()
    for _ in range(k):                            # k pasos
        mejor, mejor_delta = None, -1
        for j in range(len(S)):                   # revisa los N nodos
            if j not in A:
                delta = len(S[j] - cubierto)      # Δ_j(A): lo nuevo que trae j
                if delta > mejor_delta:
                    mejor, mejor_delta = j, delta
        A.append(mejor)                           # agrega el de mayor Δ
        cubierto |= S[mejor]
    return A, len(cubierto)

if __name__ == "__main__":
    ganancias = [[10, 6, 3, 1],    # nodo 0
                 [8, 5, 2, 1]]     # nodo 1
    print("Reparto:", reparto_voraz(ganancias, B=4))

    import math
    w = [10, 8, 7]                                # "peso" de cada nodo (cantidad/calidad de datos)
    u = lambda i, x: w[i] * math.log(1 + x)       # utilidad cóncava y creciente
    print("Reparto con u_i:", reparto_voraz_u(u, N=3, B=5))

    S = [{1, 2, 3, 4}, {1, 2, 5}, {3, 4, 6}]
    print("Selección:", seleccion_voraz(S, k=2))
