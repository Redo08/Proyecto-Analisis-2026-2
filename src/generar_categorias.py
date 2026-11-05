"""
Agrega categorías de datos sintéticas a los nodos de un caso que no las trae.

La solución base elige participantes maximizando la cobertura f(A) = |unión de las categorías de A|,
así que cada nodo necesita su conjunto de categorías. Si el caso recibido no las incluye, este
script las genera de forma reproducible (misma semilla => mismas categorías) y deja constancia del
origen en la clave "_origen_categorias" del JSON.

Uso (desde la raíz del repositorio):
    python src/generar_categorias.py casos/original.json -o casos/con_categorias.json
    python src/generar_categorias.py casos/original.json -o casos/c.json --universo 30 --min 4 --max 8 --semilla 7
"""
import argparse
import json
import random


def asignar_categorias(nodos, universo=20, minimo=3, maximo=7, semilla=2026):
    """Asigna a cada nodo un conjunto aleatorio de categorías del universo C01..C<universo>.

    Args:
        nodos:    lista de dicts de nodo (se modifica: se agrega/reemplaza la clave "categorias").
        universo: cantidad de categorías distintas posibles.
        minimo:   mínimo de categorías por nodo.
        maximo:   máximo de categorías por nodo (<= universo).
        semilla:  semilla del generador; la misma semilla produce siempre el mismo resultado.

    Returns:
        La misma lista `nodos`, con "categorias" como lista ordenada de ids ("C01", ...).
    """
    rng = random.Random(semilla)
    cats = [f"C{i:02d}" for i in range(1, universo + 1)]
    for n in nodos:
        n["categorias"] = sorted(rng.sample(cats, rng.randint(minimo, maximo)))
    return nodos


def main():
    """Interfaz de línea de comandos: lee un caso, agrega categorías y escribe el resultado."""
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", help="caso .json de partida")
    ap.add_argument("-o", "--salida", required=True, help="archivo .json a escribir")
    ap.add_argument("--universo", type=int, default=20, help="número de categorías posibles (20)")
    ap.add_argument("--min", type=int, default=3, dest="minimo", help="mínimo por nodo (3)")
    ap.add_argument("--max", type=int, default=7, dest="maximo", help="máximo por nodo (7)")
    ap.add_argument("--semilla", type=int, default=2026, help="semilla (2026)")
    a = ap.parse_args()
    if not 1 <= a.minimo <= a.maximo <= a.universo:
        ap.error("se exige 1 <= min <= max <= universo")
    with open(a.entrada, encoding="utf-8") as fh:
        d = json.load(fh)
    asignar_categorias(d["nodos"], a.universo, a.minimo, a.maximo, a.semilla)
    d["_origen_categorias"] = (f"sintéticas: semilla {a.semilla}, universo {a.universo}, "
                               f"{a.minimo} a {a.maximo} por nodo (src/generar_categorias.py)")
    with open(a.salida, "w", encoding="utf-8") as fh:
        json.dump(d, fh, indent=2, ensure_ascii=False)
    print(f"Escrito {a.salida}")


if __name__ == "__main__":
    main()
