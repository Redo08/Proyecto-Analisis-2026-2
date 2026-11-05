# Manual técnico — Solución base del Subproyecto 2 (versión 1.1.0)

Contenido: 1. Problema · 2. Algoritmos · 3. Estructura del código · 4. Formato de entrada · 5. Formato de salida y traza · 6. Pasos de ejecución · 7. Verificación de restricciones · 8. Limitaciones · 9. Correspondencia con el informe

## 1. Problema

Se tiene una red de `N` nodos. Hay dos decisiones:

1. **Selección (Parte 2).** Elegir un grupo `A` de `k` nodos entre `N` candidatos que maximice la utilidad conjunta `f(A)`. Es NP-difícil (el informe lo demuestra por reducción desde Max-Cover).
2. **Reparto (Parte 1).** Repartir `B` unidades enteras de presupuesto de ruido entre los nodos de `A` para maximizar `Σ u_i(x_i)`, con `u_i` creciente y cóncava. Se resuelve de forma exacta en tiempo polinomial.

Esta entrega es la **solución base**: un único `B` global, todos los nodos con el mismo costo de participación, una sola ejecución y sin relaciones entre nodos. Las variantes (costos de participación distintos, repetición en rondas con fallas, nodos relacionados entre sí) quedan fuera.

## 2. Algoritmos

### 2.1 Selección voraz (Algoritmo 3 del informe)

Cada nodo `j` tiene un conjunto `S_j` de **categorías de datos**. La utilidad conjunta es la cobertura:

```
f(A) = | ∪_{j ∈ A} S_j |      (cuántas categorías distintas cubre el grupo)
```

Ejemplo: con `S_1 = {a,b,c}` y `S_2 = {c,d}`, `f({1,2}) = 4`.

```
A ← ∅;  cubierto ← ∅
repetir k veces:
    para cada j ∉ A:  Δ_j = |S_j \ cubierto|           # categorías NUEVAS que aporta j
    agregar a A el j con mayor Δ_j                      # empate → menor índice
    cubierto ← cubierto ∪ S_j
```

`Δ_j` es la ganancia marginal `f(A ∪ {j}) − f(A)`. Se **recalcula en cada iteración**: un nodo con muchas categorías puede dejar de ser atractivo cuando las categorías que tenía ya están cubiertas por los nodos elegidos antes. Por eso la traza muestra, por iteración, las categorías nuevas del elegido y cómo cambió el `Δ` del mejor descartado.

Garantía: `f(A) ≥ (1 − 1/e) · f(óptimo)`, porque `f` es monótona y submodular.
Costo: `k·N` evaluaciones de `Δ`, cada una `O(s)` con `s = máx |S_j|` → **`O(k·N·s)`**.

### 2.2 Reparto voraz (Algoritmo 1 del informe)

La utilidad individual `u_i` es **configurable** (`src/utilidades.py`); `w_i` = `coeficiente_utilidad`. La ganancia marginal es `g_i(x) = u_i(x+1) − u_i(x)`. Todas las opciones cumplen lo que exige el problema (`u(0)=0`, creciente, cóncava):

| `tipo` | `u_i(x)` | Parámetro |
|---|---|---|
| `log` (por defecto) | `w_i·ln(1+x)` | — |
| `sqrt` | `w_i·(√(1+x) − 1)` | — |
| `saturacion` | `w_i·x/(1+x)` (tiende a `w_i`) | — |
| `potencia` | `w_i·((1+x)^p − 1)` | `exponente` p, `0 < p < 1` |

Se elige con la clave opcional `"funcion_utilidad": {"tipo": "saturacion"}` del JSON, o con `--utilidad saturacion` (y `--exponente 0.5` para `potencia`) en la línea de comandos, que tiene prioridad. Una función como `w_i/x` **no es válida**: es decreciente y no está definida en 0. Para otra función se agrega una entrada a `FUNCIONES` en `utilidades.py`; la validación rechaza tipos desconocidos y exponentes que rompan la concavidad.

```
x_i ← 0 para todo i;  H ← montículo de máximos con g_i(0)
repetir B veces:
    i ← extraer el máximo de H;  x_i ← x_i + 1;  insertar g_i(x_i)
```

Es **exacto** (teorema de optimalidad del informe). Costo `O(k + B·log k)` sobre los `k` nodos seleccionados (pseudo-polinomial en `B`).

## 3. Estructura del código

| Archivo | Responsabilidad |
|---|---|
| `src/entrada.py` | Lee y valida el JSON; construye `Caso` con las categorías de cada nodo como conjuntos. Lanza `ValueError` con mensaje claro si algo es inválido. |
| `src/utilidades.py` | Catálogo y validación de las funciones `u_i(x)`. |
| `src/solucion.py` | `seleccion_voraz_traza`, `reparto_voraz_traza`, `seleccion_exacta_ref` (fuerza bruta de referencia si `C(N,k) ≤ 2·10⁶`), `f_cobertura` y `resolver`. Con `traza=None` no registra nada: las decisiones son las mismas con o sin traza. |
| `src/verificacion.py` | Chequeos de restricciones (§7), incluida la comparación con `Informe/code/algoritmos.py`. |
| `src/ejecutar_casos.py` | Programa principal: recorre casos, mide tiempo, escribe `resultados/`. |
| `src/generar_categorias.py` | Agrega categorías sintéticas reproducibles a un caso que no las trae. |
| `Informe/code/algoritmos.py` | Implementación del informe. En cada ejecución se contrasta con ella la selección y el reparto. |

La lógica del algoritmo no se edita para ejecutar un caso: todo cambio de datos se hace en el JSON y todo cambio de salida en las opciones de la línea de comandos.

## 4. Formato de entrada (JSON)

```json
{
  "parametros": {
    "numero_nodos": 15,                         // debe ser igual a len(nodos)
    "cupo_participantes_por_ronda_k": 5,        // entero, 1 <= k < N
    "presupuesto_ruido_por_ronda_B": 30         // entero >= 0
  },
  "funcion_utilidad": {"tipo": "log"},          // opcional; ver §2.2 (log, sqrt, saturacion, potencia)
  "nodos": [
    {"id": "N01",
     "coeficiente_utilidad": 8.5,               // > 0 (es w_i; interviene solo en el reparto)
     "categorias": ["C11", "C17", "C19"]},      // no vacía; interviene solo en la selección
    ...
  ]
}
```

- Los ids de nodo no pueden repetirse; las categorías son textos cualesquiera (`"C11"`, `"datos_imagen"`, ...).
- **Claves ignoradas:** cualquier otra clave (por ejemplo `grafo`, `numero_rondas`, `presupuesto_total_nodo`, `costo_participacion`, `presupuesto_costos_participacion_por_ronda`, que pertenecen a variantes) se ignora sin error.
- **Si el caso no trae `categorias`,** la ejecución se detiene con un mensaje que lo indica. Para generarlas: `python src/generar_categorias.py caso.json -o caso_con_categorias.json` (opciones `--universo`, `--min`, `--max`, `--semilla`). Es reproducible: misma semilla, mismas categorías, y deja anotado el origen en la clave `_origen_categorias`.
- **Caso incluido** (`casos/entrada_G2_red_15_nodos.json`): sus nodos y coeficientes vienen de la entrada recibida; sus categorías son **sintéticas** (semilla 2026, universo de 20 categorías, entre 3 y 7 por nodo), porque la entrada recibida no las traía.

El nombre del caso es el nombre del archivo sin `.json`.

## 5. Formato de salida y traza

Por caso, en `resultados/<caso>/`:

| Archivo | Contenido |
|---|---|
| `salida.json` | versión, parámetros, entorno (Python/SO), **tiempo** (mediana, repeticiones, todas las mediciones), óptimo exacto de referencia, bandera `restricciones_ok` y `resultado`: selección, `f(A)`, reparto, utilidad y verificación. |
| `traza.md` | Traza legible: **(1)** tabla de selección con elegido, Δ, categorías nuevas que aporta, `f(A)` acumulada, 3 mejores candidatos y el seguimiento del mejor candidato descartado en la iteración anterior (Δ antes → Δ ahora); **(2)** tabla de reparto, una fila por unidad de presupuesto con nodo, ganancia marginal, `x` del nodo y siguiente ganancia; **(3)** tabla de verificación de restricciones. |
| `traza.json` | La misma traza completa en formato máquina (en selección, Δ de **todos** los candidatos en cada iteración). |

Además, `resultados/resumen.md` tiene una fila por caso: N, k, B, tiempo, `f(A)`, óptimo, estado de restricciones.

**Tiempo.** Mediana de `-r` repeticiones (por defecto 5) de resolver el caso (selección + reparto) **sin traza ni verificación**, con `time.perf_counter`. El tiempo de carga del archivo, de la referencia exacta y de la verificación no se incluye. Los tiempos varían de una máquina a otra; las decisiones no.

## 6. Pasos de ejecución

```bash
git clone <repositorio> && cd RepoProyecto
python --version                              # 3.10 o superior
python src/ejecutar_casos.py                  # genera resultados/
```

No se requieren dependencias para estos pasos (solo biblioteca estándar).

Código de salida: `0` si las restricciones se cumplen en todos los casos; `1` si alguna falla. Para casos de la profesora: copiar sus `.json` a `casos/` y ejecutar el mismo comando; para uno solo, `python src/ejecutar_casos.py ruta/al/caso.json`.
Con otra utilidad: `python src/ejecutar_casos.py --utilidad saturacion -o resultados_saturacion`.
Para regenerar gráficas y tablas del informe (opcional): `pip install -r requirements.txt` y `python Informe/code/experimentos.py`.

## 7. Verificación de restricciones

Todos los chequeos son obligatorios; si alguno falla, la ejecución termina con código 1 y la traza lo marca como `NO CUMPLE`.

| Chequeo | Qué comprueba |
|---|---|
| Tamaño de `A` = `k`, nodos distintos y válidos | Selección bien formada |
| `f(A)` de la traza = `f(A)` recalculada desde cero | La acumulación incremental es correcta |
| Ganancias de la selección no crecientes | Consecuencia de la submodularidad |
| Selección idéntica a `Informe/code/algoritmos.py` | La solución coincide con la implementación del informe |
| `Σ x = B`, `x_i` entero ≥ 0 | Reparto factible |
| Ganancias del reparto no crecientes | Concavidad observada |
| Reparto idéntico a `Informe/code/algoritmos.py` | Ídem para el reparto |
| Ninguna transferencia de 1 unidad mejora | Optimalidad local del reparto (equivale a optimalidad global por concavidad) |
| `f(voraz) ≥ (1−1/e)·f(óptimo)` | Solo si se pudo calcular el óptimo exacto |

## 8. Limitaciones

- **Costo de participación uniforme.** La selección solo respeta el cupo `k`; todos los nodos cuestan lo mismo. Los costos distintos son una variante fuera de esta entrega (con costos la cota del voraz cambia; Khuller et al., 1999).
- **Una sola ejecución.** No hay rondas, fallas de nodos ni estado entre ejecuciones.
- **Nodos independientes.** No se modelan relaciones entre nodos (grafo de influencia): la utilidad solo depende de las categorías que cubren.
- **Categorías del caso incluido sintéticas.** La entrada recibida no traía categorías; si la profesora entrega otra definición de `f`, hay que cambiar `f_cobertura` y `seleccion_voraz_traza`; el resto no cambia. `f` no usa `coeficiente_utilidad` (que solo interviene en el reparto), y los desempates dependen del orden de los nodos en el archivo.
- **Elección por defecto de `u_i` (`log`)** es una decisión de modelado del grupo; cambiable con `--utilidad` o `funcion_utilidad`.
- **Escala.** `O(k·N·s)` en selección; la fuerza bruta de referencia se omite si `C(N,k) > 2·10⁶`, y en ese caso no se verifica la garantía `(1−1/e)`.
- **Precisión.** Utilidades en `float`; las comparaciones usan tolerancia `1e-9`. `B` se trata como entero pequeño (el reparto es `O(B log k)`).
- **Tiempos** de una sola máquina, con ruido del sistema operativo; con casos de fracciones de milisegundo la desviación relativa es grande.

## 9. Correspondencia con el informe

| Informe | Código |
|---|---|
| Algoritmo 1, reparto voraz | `reparto_voraz_traza` (`Informe/code/algoritmos.py: reparto_voraz`) |
| Algoritmo 2, selección exacta | `seleccion_exacta_ref` (por combinaciones) |
| Algoritmo 3, selección voraz | `seleccion_voraz_traza` (`Informe/code/algoritmos.py: seleccion_voraz`) |
| Utilidad de cobertura `f(A)=\|∪ S_j\|` | `f_cobertura` |
| Variantes (costos de participación, rondas con fallas, nodos relacionados) | Fuera de esta entrega; ver §8 |
