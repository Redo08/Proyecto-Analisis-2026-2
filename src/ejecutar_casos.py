"""
Ejecuta la solución base sobre uno o varios casos y escribe salida, tiempo y traza por caso.

Uso (desde la raíz del repositorio):
    python src/ejecutar_casos.py                       # todos los .json de casos/
    python src/ejecutar_casos.py casos/mi_caso.json    # un caso
    python src/ejecutar_casos.py casos/ -r 10 -o resultados
    python src/ejecutar_casos.py --utilidad saturacion -o resultados_sat     # otra u_i(x)

Por cada caso crea  resultados/<caso>/{salida.json, traza.json, traza.md}  y al final resultados/resumen.md
Código de salida: 0 si todas las restricciones se cumplen en todos los casos, 1 si no.
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

from entrada import cargar                          # noqa: E402
from solucion import resolver, seleccion_exacta_ref  # noqa: E402
from utilidades import construir, describir, FUNCIONES  # noqa: E402
from verificacion import verificar                  # noqa: E402


def version():
    """Versión de la entrega (contenido del archivo VERSION de la raíz). Se estampa en todas las salidas."""
    with open(os.path.join(RAIZ, "VERSION"), encoding="utf-8") as fh:
        return fh.read().strip()


def medir(caso, repeticiones):
    """Mide el tiempo de resolver el caso (selección + reparto) SIN traza ni verificación.

    Args:
        caso:         `Caso` validado.
        repeticiones: cuántas veces se ejecuta.

    Returns:
        (mediana, tiempos): segundos medidos con time.perf_counter; `tiempos` son todas las mediciones.
    """
    ts = []
    for _ in range(repeticiones):
        t0 = time.perf_counter()
        resolver(caso)
        ts.append(time.perf_counter() - t0)
    return statistics.median(ts), ts


def ejecutar_caso(ruta, repeticiones, utilidad=None):
    """Carga un caso, mide su tiempo y lo resuelve una vez con traza y verificación.

    Args:
        ruta:         archivo .json del caso.
        repeticiones: repeticiones para la mediana de tiempo.
        utilidad:     especificación de u_i(x) que reemplaza a la del archivo (None = la del archivo).

    Returns:
        (caso, ref, t, ts, res): `ref` es el óptimo exacto (f*, A*) o None; `t` y `ts` son la mediana y
        todas las mediciones de tiempo; `res` es un dict con la selección, f(A), el reparto, la utilidad,
        las trazas y la verificación (los nodos van por id).

    Raises:
        ValueError / KeyError / OSError: el caso es inválido o no se puede leer (ver entrada.cargar).
    """
    caso = cargar(ruta, utilidad)
    t, ts = medir(caso, repeticiones)
    ref = seleccion_exacta_ref(caso.S, caso.k)
    tr_sel, tr_rep = [], []
    A, fA, x = resolver(caso, tr_sel, tr_rep)
    u = construir(caso.utilidad, [caso.coef[j] for j in A])
    res = dict(
        seleccion=[caso.ids[j] for j in A], f_A=fA,
        reparto={caso.ids[j]: x[i] for i, j in enumerate(A)},
        utilidad_reparto=sum(u(i, x[i]) for i in range(len(A))),
        traza_seleccion=[dict(t_, deltas={caso.ids[j]: d for j, d in t_["deltas"].items()},
                              elegido=caso.ids[t_["elegido"]]) for t_ in tr_sel],
        traza_reparto=[dict(t_, nodo=caso.ids[A[t_["nodo"]]]) for t_ in tr_rep],
        verificacion=verificar(caso, A, fA, x, tr_sel, tr_rep, ref))
    return caso, ref, t, ts, res


def escribir(caso, ref, t, ts, res, repeticiones, dir_caso):
    """Escribe salida.json, traza.json y traza.md en `dir_caso` (se crea si no existe).

    salida.json lleva el resultado, el tiempo y la verificación; traza.json y traza.md llevan la traza
    completa (formato máquina y formato legible).

    Returns:
        El dict de salida.json (incluye `restricciones_ok`).
    """
    os.makedirs(dir_caso, exist_ok=True)
    ok = all(c["cumple"] for c in res["verificacion"])
    salida = dict(
        version=version(), caso=caso.nombre,
        parametros=dict(N=caso.N, k=caso.k, B=caso.B,
                        funcion_utilidad=dict(caso.utilidad, formula=describir(caso.utilidad))),
        entorno=dict(python=platform.python_version(), sistema=platform.platform()),
        tiempo=dict(mediana_s=t, repeticiones=repeticiones, todas_s=ts),
        referencia_exacta=None if ref is None else dict(f_optimo=ref[0], A=[caso.ids[j] for j in ref[1]]),
        restricciones_ok=ok,
        resultado={k: v for k, v in res.items() if not k.startswith("traza")})
    traza = dict(version=version(), caso=caso.nombre, seleccion=res["traza_seleccion"],
                 reparto=res["traza_reparto"], verificacion=res["verificacion"])
    for nombre, obj in (("salida.json", salida), ("traza.json", traza)):
        with open(os.path.join(dir_caso, nombre), "w", encoding="utf-8") as fh:
            json.dump(obj, fh, indent=2, ensure_ascii=False)
    with open(os.path.join(dir_caso, "traza.md"), "w", encoding="utf-8") as fh:
        fh.write(traza_md(caso, ref, res))
    return salida


def traza_md(caso, ref, res):
    """Genera el texto Markdown de la traza: (1) selección con ganancias marginales y categorías nuevas,
    (2) reparto del presupuesto paso a paso y (3) tabla de verificación de restricciones."""
    L = [f"# Traza del caso `{caso.nombre}` (versión {version()})", "",
         f"N={caso.N}, k={caso.k}, B={caso.B}. u_i(x) = {describir(caso.utilidad)}. "
         "Desempates: menor índice.", "",
         "## 1. Selección de nodos (voraz por ganancia marginal Δ)", "",
         "Δ de un candidato = cuántas categorías **nuevas** aporta, es decir, las que su conjunto tiene y "
         "aún no cubren los ya elegidos. Se recalcula en cada iteración (por eso un nodo con Δ alto al "
         "inicio puede aportar poco después). La última columna sigue al mejor candidato descartado en "
         "la iteración anterior.", "",
         "| Iter | Elegido | Δ | Categorías nuevas | f(A) acumulada | Mejores 3 candidatos (nodo: Δ) "
         "| Mejor descartado antes (Δ antes → Δ ahora) |",
         "|---|---|---|---|---|---|---|"]
    ts = res["traza_seleccion"]
    for n, t in enumerate(ts):
        top = sorted(t["deltas"].items(), key=lambda kv: -kv[1])[:3]
        if n == 0:
            seguido = "—"
        else:
            prev = ts[n - 1]
            desc = {c: d for c, d in prev["deltas"].items() if c != prev["elegido"]}
            c = max(desc, key=lambda q: desc[q])      # empate: el primero (menor índice)
            seguido = f"{c} ({desc[c]} → {t['deltas'].get(c, 0)})"
        L.append(f"| {t['iteracion']} | {t['elegido']} | {t['ganancia']} | {', '.join(t['nuevas'])} | "
                 f"{t['f_acumulada']} | " + ", ".join(f"{q}: {d}" for q, d in top) + f" | {seguido} |")
    razon = "" if ref is None else f"  (óptimo exacto f* = {ref[0]}, razón {res['f_A'] / ref[0]:.4f})"
    L += ["", f"A = {res['seleccion']},  f(A) = {res['f_A']}{razon}", "",
          "## 2. Reparto del presupuesto de ruido (una unidad por paso al mayor g_i(x))", "",
          "| Paso | Nodo | Ganancia marginal g | x del nodo | Próxima ganancia del nodo |",
          "|---|---|---|---|---|"]
    for t in res["traza_reparto"]:
        L.append(f"| {t['paso']} | {t['nodo']} | {t['ganancia']:.4f} | {t['x_nodo']} | "
                 f"{t['proxima_ganancia']:.4f} |")
    L += ["", "Reparto final: " + ", ".join(f"{n}={v}" for n, v in res["reparto"].items())
          + f"  (suma = {sum(res['reparto'].values())}, utilidad = {res['utilidad_reparto']:.4f})", "",
          "## 3. Verificación de restricciones", "",
          "| Restricción | Esperado | Obtenido | Resultado |", "|---|---|---|---|"]
    for c in res["verificacion"]:
        L.append(f"| {c['nombre']} | {c['esperado']} | {c['obtenido']} | "
                 f"{'CUMPLE' if c['cumple'] else '**NO CUMPLE**'} |")
    return "\n".join(L) + "\n"


def main():
    """Interfaz de línea de comandos: ejecuta los casos, escribe resultados/ y resumen.md.

    Termina con código 0 si las restricciones se cumplen en todos los casos, 1 si no, y con un mensaje
    de error (sin traceback) si un caso es inválido.
    """
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
            caso, ref, t, ts, res = ejecutar_caso(ruta, a.repeticiones, spec)
        except (ValueError, KeyError, OSError) as e:
            sys.exit(f"Error en {ruta}: {e}")
        s = escribir(caso, ref, t, ts, res, a.repeticiones, os.path.join(a.salida, caso.nombre))
        filas.append((caso.nombre, caso.N, caso.k, caso.B, t, res["f_A"], ref[0] if ref else None,
                      s["restricciones_ok"]))
        print(f"{caso.nombre}: tiempo = {t * 1e3:.3f} ms | f(A) = {res['f_A']} | "
              f"restricciones: {'OK' if s['restricciones_ok'] else 'FALLAN'}")
    L = [f"# Resumen de ejecución (versión {version()})", "",
         f"Python {platform.python_version()}, {platform.platform()}. "
         f"Tiempo = mediana de {a.repeticiones} repeticiones (selección + reparto, sin traza).", "",
         "| Caso | N | k | B | Tiempo (ms) | f(A) | f óptimo | Restricciones |", "|---|---|---|---|---|---|---|---|"]
    for n, N, k, B, t, f, fo, ok in filas:
        L.append(f"| {n} | {N} | {k} | {B} | {t * 1e3:.3f} | {f} | {'' if fo is None else fo} | "
                 f"{'OK' if ok else 'FALLAN'} |")
    with open(os.path.join(a.salida, "resumen.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print(f"Resultados en {a.salida}")
    sys.exit(0 if all(f[7] for f in filas) else 1)


if __name__ == "__main__":
    main()
