"""
Validación experimental del Subproyecto 2 (solución base).

Ejecutar desde la carpeta del informe:   python code/experimentos.py
Genera:  img/*.png  (gráficas)  y  code/resultados.json  (tablas)

Todas las instancias son sintéticas y se generan con semillas fijas.
"""
import gc
import json
import math
import os
import random
import statistics
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from algoritmos import (reparto_voraz, utilidad_log, utilidad_total,
                        seleccion_exacta, seleccion_voraz)

SEMILLA = 2026
REPETICIONES = 5
AQUI = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(AQUI, "..", "img")
os.makedirs(IMG, exist_ok=True)

AZUL, DORADO = "#1f5fa8", "#c49a28"


# ---------------------------------------------------------------- generadores
def instancia_reparto(N, semilla):
    """N pesos w_i ~ U[1, 100]; u_i(x) = w_i ln(1 + x)."""
    rng = random.Random(semilla)
    return [rng.uniform(1, 100) for _ in range(N)]


def instancia_cobertura(N, tam_U, s_min, s_max, semilla):
    """N conjuntos S_j de tamaño aleatorio en [s_min, s_max] tomados de U = {0..tam_U-1}."""
    rng = random.Random(semilla)
    return [set(rng.sample(range(tam_U), rng.randint(s_min, s_max))) for _ in range(N)]


def medir(fn, *args):
    """Mediana de REPETICIONES ejecuciones, en segundos.
    Se desactiva el recolector de basura durante la medición (como hace timeit)."""
    tiempos = []
    for _ in range(REPETICIONES):
        gc.collect()
        gc.disable()
        t0 = time.perf_counter()
        fn(*args)
        tiempos.append(time.perf_counter() - t0)
        gc.enable()
    return statistics.median(tiempos)


# ---------------------------------------------------------------- experimentos
def exp_reparto_N():
    """Parte 1: se varía N con B = 10 N. Teoría: g = N + B log2 N."""
    filas = []
    for N in [1000, 2000, 4000, 8000, 16000, 32000, 64000]:
        B = 10 * N
        u = utilidad_log(instancia_reparto(N, SEMILLA + N))
        t = medir(reparto_voraz, u, N, B)
        g = N + B * math.log2(N)
        filas.append(dict(N=N, B=B, t=t, g=g, r=t / g))
    return filas


def exp_reparto_B():
    """Parte 1: N fijo, se varía B. Teoría: lineal en B."""
    filas, N = [], 1000
    u = utilidad_log(instancia_reparto(N, SEMILLA))
    for B in [10_000, 20_000, 40_000, 80_000, 160_000, 320_000]:
        t = medir(reparto_voraz, u, N, B)
        g = N + B * math.log2(N)
        filas.append(dict(N=N, B=B, t=t, g=g, r=t / g))
    return filas


def exp_voraz_N():
    """Parte 2, voraz: k = 20 fijo, se varía N. Teoría: (kN - k(k-1)/2) evaluaciones, tau = O(s)."""
    filas, k = [], 20
    for N in [500, 1000, 2000, 4000, 8000, 16000]:
        S = instancia_cobertura(N, 1000, 10, 30, SEMILLA + N)
        t = medir(seleccion_voraz, S, k)
        _, _, ev = seleccion_voraz(S, k)
        g = k * N - k * (k - 1) // 2
        filas.append(dict(N=N, k=k, t=t, ev=ev, g=g, r=t / g))
    return filas


def exp_voraz_k():
    """Parte 2, voraz: N = 2000 fijo, se varía k."""
    filas, N = [], 2000
    S = instancia_cobertura(N, 1000, 10, 30, SEMILLA)
    for k in [10, 20, 40, 80, 160, 320]:
        t = medir(seleccion_voraz, S, k)
        _, _, ev = seleccion_voraz(S, k)
        g = k * N - k * (k - 1) // 2
        filas.append(dict(N=N, k=k, t=t, ev=ev, g=g, r=t / g))
    return filas


def exp_exacto():
    """Parte 2, exacto: k = N/2. Teoría: C(N,k) hojas, cada una con tau = O(k s)."""
    filas = []
    global REPETICIONES
    rep = REPETICIONES
    REPETICIONES = 3
    for N in [8, 10, 12, 14, 16, 18, 20]:
        k = N // 2
        S = instancia_cobertura(N, 60, 3, 8, SEMILLA + N)
        t = medir(seleccion_exacta, S, k)
        _, _, ev = seleccion_exacta(S, k)
        g = math.comb(N, k)
        filas.append(dict(N=N, k=k, t=t, ev=ev, comb=g, g=g * k, r=t / (g * k)))
    REPETICIONES = rep
    return filas


def exp_razon():
    """Garantía (1 - 1/e): 100 instancias pequeñas por configuración."""
    filas = []
    for N, k in [(10, 3), (12, 4), (14, 5), (16, 6), (18, 6)]:
        razones = []
        for rep in range(100):
            S = instancia_cobertura(N, 25, 2, 7, SEMILLA * 1000 + N * 100 + rep)
            opt, _, _ = seleccion_exacta(S, k)
            vor, _, _ = seleccion_voraz(S, k)
            razones.append(vor / opt)
        filas.append(dict(N=N, k=k, minimo=min(razones), media=statistics.mean(razones),
                          optimos=sum(r == 1 for r in razones), n=len(razones)))
    return filas


def verifica_reparto_optimo():
    """Comprueba el Teorema de optimalidad contra fuerza bruta en instancias pequeñas."""
    import itertools
    casos, iguales = 0, 0
    for rep in range(200):
        rng = random.Random(SEMILLA + rep)
        N, B = rng.randint(2, 4), rng.randint(1, 8)
        u = utilidad_log([rng.uniform(1, 100) for _ in range(N)])
        v = utilidad_total(u, reparto_voraz(u, N, B))
        mejor = max(utilidad_total(u, x)
                    for x in itertools.product(range(B + 1), repeat=N) if sum(x) <= B)
        casos += 1
        iguales += abs(v - mejor) < 1e-9
    return dict(casos=casos, iguales=iguales)


# ---------------------------------------------------------------- gráficas
def estilo(ax, titulo, xlabel, ylabel):
    ax.set_title(titulo, fontsize=11, loc="left")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, which="major", color="#e3e3e3", linewidth=0.8)
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)


def grafica_medido_vs_teoria(filas, xkey, titulo, xlabel, archivo, logx=True, logy=True):
    """Tiempo medido (puntos) y c * g(n) (línea). La constante c es la media
    geométrica de los cocientes r = t / g (ajuste por mínimos cuadrados en escala log)."""
    x = [f[xkey] for f in filas]
    t = [f["t"] for f in filas]
    c = math.exp(statistics.mean(math.log(f["r"]) for f in filas))
    teo = [c * f["g"] for f in filas]
    fig, ax = plt.subplots(figsize=(6.2, 3.6))
    ax.plot(x, teo, color=DORADO, linewidth=2, label="teoría: $c\\cdot g(n)$")
    ax.plot(x, t, "o", color=AZUL, markersize=7, label="medido")
    if logx:
        ax.set_xscale("log", base=2)
    if logy:
        ax.set_yscale("log")
    estilo(ax, titulo, xlabel, "tiempo (s)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, archivo), dpi=200)
    plt.close(fig)


def grafica_razon(filas, archivo):
    etiquetas = [f"N={f['N']}\nk={f['k']}" for f in filas]
    fig, ax = plt.subplots(figsize=(6.2, 3.4))
    xs = range(len(filas))
    ax.plot(xs, [f["media"] for f in filas], "o-", color=AZUL, linewidth=2, markersize=7, label="razón media")
    ax.plot(xs, [f["minimo"] for f in filas], "s--", color=DORADO, linewidth=2, markersize=7, label="razón mínima")
    ax.axhline(1 - 1 / math.e, color="#555555", linewidth=1.2, linestyle=":")
    ax.text(len(filas) - 1, 1 - 1 / math.e + 0.012, "cota $1-1/e\\approx0.632$", ha="right", fontsize=9, color="#555555")
    ax.set_xticks(list(xs))
    ax.set_xticklabels(etiquetas, fontsize=8)
    ax.set_ylim(0.55, 1.03)
    estilo(ax, "Voraz frente al óptimo (100 instancias por configuración)", "", "$f(A_g)/f(A^*)$")
    ax.legend(frameon=False, loc="center left", bbox_to_anchor=(0.0, 0.45))
    fig.tight_layout()
    fig.savefig(os.path.join(IMG, archivo), dpi=200)
    plt.close(fig)


if __name__ == "__main__":
    R = {}
    print("Parte 1, variando N ...");  R["reparto_N"] = exp_reparto_N()
    print("Parte 1, variando B ...");  R["reparto_B"] = exp_reparto_B()
    print("Parte 1, optimalidad ..."); R["reparto_opt"] = verifica_reparto_optimo()
    print("Parte 2 voraz, N ...");     R["voraz_N"] = exp_voraz_N()
    print("Parte 2 voraz, k ...");     R["voraz_k"] = exp_voraz_k()
    print("Parte 2 exacto ...");       R["exacto"] = exp_exacto()
    print("Parte 2 razón ...");        R["razon"] = exp_razon()

    with open(os.path.join(AQUI, "resultados.json"), "w") as fh:
        json.dump(R, fh, indent=2)

    grafica_medido_vs_teoria(R["reparto_N"], "N", "Parte 1: reparto voraz ($B=10N$)", "$N$", "reparto_N.png")
    grafica_medido_vs_teoria(R["reparto_B"], "B", "Parte 1: reparto voraz ($N=1000$)", "$B$", "reparto_B.png")
    grafica_medido_vs_teoria(R["voraz_N"], "N", "Parte 2: selección voraz ($k=20$)", "$N$", "voraz_N.png")
    grafica_medido_vs_teoria(R["voraz_k"], "k", "Parte 2: selección voraz ($N=2000$)", "$k$", "voraz_k.png")
    grafica_medido_vs_teoria(R["exacto"], "N", "Parte 2: selección exacta ($k=N/2$)", "$N$", "exacto.png", logx=False)
    grafica_razon(R["razon"], "razon.png")
    print(json.dumps(R, indent=1))
