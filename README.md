# Proyecto Análisis de Algoritmos 2026-2 — Subproyecto 2: solución base

Selección de participantes y reparto del presupuesto de ruido en una red de aprendizaje colaborativo.
**Versión 1.1.0** (archivo [VERSION](VERSION)).

## Ejecutar

Requisito: **Python 3.10 o superior**. No hay que instalar nada: la ejecución de casos solo usa la biblioteca estándar.

```bash
git clone <repositorio> && cd RepoProyecto
python src/ejecutar_casos.py                  # 1. ejecuta todos los casos de casos/
```
2. Abrir `resultados/resumen.md` y `resultados/<caso>/traza.md`.

| Quiero... | Comando |
|---|---|
| Ejecutar un solo caso | `python src/ejecutar_casos.py casos/otro.json` |
| Más repeticiones para el tiempo / otra carpeta de salida | `python src/ejecutar_casos.py -r 10 -o mis_resultados` |
| Cambiar la función de utilidad (log, sqrt, saturacion, potencia) | `python src/ejecutar_casos.py --utilidad saturacion` (o la clave `funcion_utilidad` del JSON; ver manual §2.2) |
| Ver todas las opciones | `python src/ejecutar_casos.py --help` |
| Agregar categorías a un caso que no las trae | `python src/generar_categorias.py caso.json -o caso_con_categorias.json` |
| Regenerar gráficas del informe (opcional) | `pip install -r requirements.txt` y `python Informe/code/experimentos.py` |

En Windows, si `python` no se reconoce, usar `py`. Para agregar un caso basta con copiar su `.json` a `casos/` y volver a ejecutar; no hay que editar código.
`matplotlib` (`requirements.txt`) es únicamente para las gráficas del informe.

## Dónde está cada cosa

| Qué busco | Dónde |
|---|---|
| Manual técnico (algoritmo, código, formatos, limitaciones) | [docs/manual_tecnico.md](docs/manual_tecnico.md) |
| Informe teórico (LaTeX y PDF) | [Informe/main.pdf](Informe/main.pdf), fuentes en `Informe/tex/` |
| Casos de entrada | [casos/](casos/) |
| Resumen de resultados y tiempos | [resultados/resumen.md](resultados/resumen.md) |
| Salida, tiempo y verificación de un caso | `resultados/<caso>/salida.json` |
| Traza legible (selección, ganancias marginales, reparto, restricciones) | `resultados/<caso>/traza.md` (misma información en `traza.json`) |
| Algoritmos del informe (Parte 1 y 2) | [Informe/code/algoritmos.py](Informe/code/algoritmos.py) |
| Código que aplica la solución a un caso | [src/](src/) |
| Funciones de utilidad u_i(x) disponibles | [src/utilidades.py](src/utilidades.py) |
| Agregar categorías a un caso que no las trae | [src/generar_categorias.py](src/generar_categorias.py) (ver manual §4) |
| Experimentos y gráficas del informe | [Informe/code/experimentos.py](Informe/code/experimentos.py) (requiere `pip install -r requirements.txt`) |

## Resultado del caso incluido (`entrada_G2_red_15_nodos`)

Los coeficientes de utilidad vienen de la entrada recibida; las **categorías de cada nodo son sintéticas** (la entrada no las traía; se generaron con semilla 2026, ver manual §4).

- Selección: N03, N10, N08, N09, N01 con f(A) = 20 categorías cubiertas (coincide con el óptimo exacto).
- Reparto de B = 30 (con la utilidad por defecto `log`): N03=5, N10=8, N08=6, N09=6, N01=5 (utilidad 98.67).
- Todas las restricciones se cumplen, incluida la coincidencia con las implementaciones de `Informe/code/algoritmos.py`.
- Es la solución **base**: no incluye las variantes (costos de participación distintos, rondas con fallas, nodos relacionados). Si un caso trae esos campos (`grafo`, `numero_rondas`, costos...), se ignoran.

## Estructura

```
VERSION  README.md  requirements.txt
casos/        entradas .json
src/          entrada.py, utilidades.py, solucion.py, verificacion.py, ejecutar_casos.py, generar_categorias.py
resultados/   generado por ejecutar_casos.py
docs/         manual_tecnico.md
Informe/      informe LaTeX, code/ (algoritmos del informe y experimentos)
```

## Consistencia de versión

Informe, código, manual y resultados corresponden a la versión de `VERSION`; cada `salida.json`, `traza.*` y `resumen.md` la incluye. Al cambiar el código o los casos, se actualiza `VERSION` y se regeneran los resultados con el comando del paso 1.
