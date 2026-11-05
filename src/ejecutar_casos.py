"""
Ejecuta la solución base sobre uno o varios casos y escribe salida, tiempo y traza por caso.

Uso (desde la raíz del repositorio):
    python src/ejecutar_casos.py                       # todos los .json de casos/
    python src/ejecutar_casos.py casos/mi_caso.json    # un caso
    python src/ejecutar_casos.py casos/ -r 10 -o resultados
    python src/ejecutar_casos.py --utilidad saturacion -o resultados_sat     # otra u_i(x)

Por cada caso crea  resultados/<caso>/{salida.json, traza.json, traza.md}  y al final resultados/resumen.md
Código de salida: 0 si todas las restricciones obligatorias se cumplen en todos los casos, 1 si no.
"""
import argparse
import glob
import json
import os
import platform
import statistics
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(AQUI)
sys.path.insert(0, AQUI)

from entrada import cargar                                   # noqa: E402
from solucion import resolver_ronda, seleccion_exacta_ref    # noqa: E402
from utilidades import construir, describir, FUNCIONES      # noqa: E402
from verificacion import verificar_ronda                     # noqa: E402


def version():
    with open(os.path.join(RAIZ, "VERSION"), encoding="utf-8") as fh:
        return fh.read().strip()


def medir(caso, repeticiones):
    """Tiempos (s) de una ronda SIN traza; devuelve (mediana, todos)."""
    ts = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        resolver_ronda(caso)
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts), ts


def ejecutar_caso(ruta, repeticiones, utilidad=None):
    caso = cargar(ruta, utilidad)
    t_ronda, ts = medir(caso, repeticiones)
    ref = seleccion_exacta_ref(caso.P, caso.k)
    rondas, acumulado = [], [0] * caso.N
    u_sel = lambda A: construir(caso.utilidad, [caso.coef[j] for j in A])
    for r in range(1, caso.rondas + 1):
        tr_sel, tr_rep = [], []
        A, fA, x = resolver_ronda(caso, tr_sel, tr_rep)
        checks = verificar_ronda(caso, A, fA, x, tr_sel, tr_rep, ref, acumulado)
        for i, j in enumerate(A):
            acumulado[j] += x[i]
        rondas.append(dict(
            ronda=r,
            seleccion=[caso.ids[j] for j in A], f_A=fA,
            reparto={caso.ids[j]: x[i] for i, j in enumerate(A)},
            utilidad_reparto=sum(u_sel(A)(i, x[i]) for i in range(len(A))),
            costo_participacion=sum(caso.costo[j] for j in A),
            traza_seleccion=[dict(t, deltas={caso.ids[j]: d for j, d in t["deltas"].items()},
                                  elegido=caso.ids[t["elegido"]]) for t in tr_sel],
            traza_reparto=[dict(t, nodo=caso.ids[A[t["nodo"]]]) for t in tr_rep],
            verificacion=checks))
    return caso, ref, t_ronda, ts, rondas


def escribir(caso, ref, t_ronda, ts, rondas, repeticiones, dir_caso):
    os.makedirs(dir_caso, exist_ok=True)
    ok = all(c["cumple"] for r in rondas for c in r["verificacion"] if c["tipo"] == "obligatoria")
    info = sorted({c["nombre"] for r in rondas for c in r["verificacion"]
                   if c["tipo"] == "informativa" and not c["cumple"]})
    salida = dict(
        version=version(), caso=caso.nombre,
        parametros=dict(N=caso.N, rondas=caso.rondas, k=caso.k, B=caso.B, B_costos=caso.B_costos,
                        funcion_utilidad=dict(caso.utilidad, formula=describir(caso.utilidad))),
        entorno=dict(python=platform.python_version(), sistema=platform.platform()),
        tiempo=dict(mediana_por_ronda_s=t_ronda, repeticiones=repeticiones, todas_s=ts,
                    total_rondas_s=t_ronda * caso.rondas),
        referencia_exacta=None if ref is None else dict(f_optimo=ref[0], A=[caso.ids[j] for j in ref[1]]),
        restricciones_obligatorias_ok=ok, restricciones_informativas_incumplidas=info,
        rondas=[{k: v for k, v in r.items() if not k.startswith("traza")} for r in rondas])
    traza = dict(version=version(), caso=caso.nombre,
                 rondas=[dict(ronda=r["ronda"], seleccion=r["traza_seleccion"], reparto=r["traza_reparto"],
                              verificacion=r["verificacion"]) for r in rondas])
    for nombre, obj in (("salida.json", salida), ("traza.json", traza)):
        with open(os.path.join(dir_caso, nombre), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(dir_caso, "traza.md"), "w", encoding="utf-8") as fh:
        fh.write(traza_md(caso, ref, rondas))
    return salida


def traza_md(caso, ref, rondas):
    L = [f"# Traza del caso `{caso.nombre}` (versión {version()})", "",
         f"N={caso.N}, rondas={caso.rondas}, k={caso.k}, B={caso.B}. "
         f"u_i(x) = {describir(caso.utilidad)}. Desempates: menor índice.", ""]
    for r in rondas:
        L += [f"## Ronda {r['ronda']}", "", "### 1. Selección de nodos (voraz por ganancia marginal Δ)", "",
              "| Iter | Elegido | Δ del elegido | f(A) acumulada | Mejores 3 candidatos (nodo: Δ) |",
              "|---|---|---|---|---|"]
        for t in r["traza_seleccion"]:
            top = sorted(t["deltas"].items(), key=lambda kv: -kv[1])[:3]
            L.append(f"| {t['iteracion']} | {t['elegido']} | {t['ganancia']:.4f} | {t['f_acumulada']:.4f} | "
                     + ", ".join(f"{n}: {d:.3f}" for n, d in top) + " |")
        razon = "" if ref is None else f"  (óptimo exacto f* = {ref[0]:.4f}, razón {r['f_A'] / ref[0]:.4f})"
        L += ["", f"A = {r['seleccion']},  f(A) = {r['f_A']:.4f}{razon}", "",
              "### 2. Reparto del presupuesto de ruido (una unidad por paso al mayor g_i(x))", "",
              "| Paso | Nodo | Ganancia marginal g | x del nodo | Próxima ganancia del nodo |",
              "|---|---|---|---|---|"]
        for t in r["traza_reparto"]:
            L.append(f"| {t['paso']} | {t['nodo']} | {t['ganancia']:.4f} | {t['x_nodo']} | "
                     f"{t['proxima_ganancia']:.4f} |")
        L += ["", "Reparto final: " + ", ".join(f"{n}={v}" for n, v in r["reparto"].items())
              + f"  (suma = {sum(r['reparto'].values())}, utilidad = {r['utilidad_reparto']:.4f})", "",
              "### 3. Verificación de restricciones", "",
              "| Restricción | Tipo | Esperado | Obtenido | Resultado |", "|---|---|---|---|---|"]
        for c in r["verificacion"]:
            if c["cumple"]:
                res = "CUMPLE"
            else:
                res = "**NO CUMPLE**" if c["tipo"] == "obligatoria" else "**NO CUMPLE (informativa)**"
            L.append(f"| {c['nombre']} | {c['tipo']} | {c['esperado']} | {c['obtenido']} | {res} |")
        L.append("")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entradas", nargs="*", default=[os.path.join(RAIZ, "casos")],
                    help="archivos .json y/o carpetas (por defecto casos/)")
    ap.add_argument("-o", "--salida", default=os.path.join(RAIZ, "resultados"))
    ap.add_argument("-r", "--repeticiones", type=int, default=5, help="repeticiones para la mediana de tiempo")
    ap.add_argument("--utilidad", choices=sorted(FUNCIONES),
                    help="función u_i(x) para todos los casos (por defecto la del JSON, o log)")
    ap.add_argument("--exponente", type=float, help="p de la función 'potencia' (0 < p < 1)")
    a = ap.parse_args()
    spec = None
    if a.utilidad:
        spec = {"tipo": a.utilidad}
        if a.exponente is not None:
            spec["exponente"] = a.exponente

    archivos = []
    for e in a.entradas:
        archivos += sorted(glob.glob(os.path.join(e, "*.json"))) if os.path.isdir(e) else [e]
    if not archivos:
        sys.exit("No se encontraron casos .json")

    filas = []
    for ruta in archivos:
        try:
            caso, ref, t, ts, rondas = ejecutar_caso(ruta, a.repeticiones, spec)
        except (ValueError, KeyError, OSError) as e:
            sys.exit(f"Error en {ruta}: {e}")
        s = escribir(caso, ref, t, ts, rondas, a.repeticiones, os.path.join(a.salida, caso.nombre))
        r1 = rondas[0]
        filas.append((caso.nombre, caso.N, caso.k, caso.B, t, r1["f_A"], ref[0] if ref else None,
                      s["restricciones_obligatorias_ok"], s["restricciones_informativas_incumplidas"]))
        print(f"{caso.nombre}: tiempo/ronda = {t * 1e3:.3f} ms | f(A) = {r1['f_A']:.4f} | "
              f"restricciones obligatorias: {'OK' if s['restricciones_obligatorias_ok'] else 'FALLAN'}")
    L = [f"# Resumen de ejecución (versión {version()})", "",
         f"Python {platform.python_version()}, {platform.platform()}. "
         f"Tiempo = mediana de {a.repeticiones} repeticiones de una ronda, sin traza.", "",
         "| Caso | N | k | B | Tiempo/ronda (ms) | f(A) | f óptimo | Obligatorias | Informativas incumplidas |",
         "|---|---|---|---|---|---|---|---|---|"]
    for n, N, k, B, t, f, fo, ok, inf in filas:
        L.append(f"| {n} | {N} | {k} | {B} | {t * 1e3:.3f} | {f:.4f} | {'' if fo is None else f'{fo:.4f}'} | "
                 f"{'OK' if ok else 'FALLAN'} | {'; '.join(inf) if inf else 'ninguna'} |")
    with open(os.path.join(a.salida, "resumen.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"Resultados en {a.salida}")
    sys.exit(0 if all(f[7] for f in filas) else 1)


if __name__ == "__main__":
    main()
