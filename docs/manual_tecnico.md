# Manual técnico — Solución base del Subproyecto 2 (versión 1.1.0)

Contenido: 1. Problema · 2. Algoritmos · 3. Explicación del código · 4. Formato de entrada · 5. Formato de salida y traza · 6. Pasos de ejecución · 7. Verificación de restricciones · 8. Limitaciones · 9. Correspondencia con el informe

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

## 3. Explicación del código

Esta sección recorre el código real, en el orden en que se ejecuta, y lo conecta con los algoritmos de la sección 2. Los números de los ejemplos salen del caso incluido (`casos/entrada_G2_red_15_nodos.json`) y se pueden comprobar en `resultados/entrada_G2_red_15_nodos/traza.md`.

### 3.1 Qué hace cada archivo

| Archivo | Responsabilidad |
|---|---|
| `src/ejecutar_casos.py` | **Programa principal.** Lee los argumentos, recorre los casos, mide el tiempo, llama a la solución y escribe `resultados/`. |
| `src/entrada.py` | Lee y valida el JSON; construye el objeto `Caso`. Lanza `ValueError` con mensaje claro si algo es inválido. |
| `src/solucion.py` | **El núcleo.** Los dos algoritmos voraces (`seleccion_voraz_traza`, `reparto_voraz_traza`), la utilidad `f_cobertura`, el óptimo de referencia `seleccion_exacta_ref` (fuerza bruta, solo si `C(N,k) ≤ 2·10⁶`) y `resolver`, que los une. |
| `src/utilidades.py` | Catálogo de funciones `u_i(x)` y su validación. |
| `src/verificacion.py` | Chequeos de restricciones (§7), incluida la comparación con `Informe/code/algoritmos.py`. |
| `src/generar_categorias.py` | Herramienta aparte: agrega categorías sintéticas reproducibles a un caso que no las trae. |
| `Informe/code/algoritmos.py` | Implementación del informe. No la usa la solución; solo se contrasta con ella en cada ejecución. |

La lógica del algoritmo no se edita para ejecutar un caso: los datos se cambian en el JSON y la salida con las opciones de la línea de comandos.

### 3.2 Flujo completo de una ejecución

```
python src/ejecutar_casos.py
        │
        ▼
 main()                          lee argumentos y lista los .json de casos/
        │   (por cada caso)
        ▼
 ejecutar_caso(ruta)
   ├─ cargar(ruta)               entrada.py   → objeto Caso (valida todo)
   ├─ medir(caso)                resolver() varias veces SIN traza → mediana de tiempo
   ├─ seleccion_exacta_ref()     óptimo por fuerza bruta (si C(N,k) es pequeño)
   ├─ resolver(caso, trazas)     solucion.py  → selección + reparto, CON traza
   │     ├─ seleccion_voraz_traza(S, k)          elige los k nodos
   │     └─ reparto_voraz_traza(w, B, spec)      reparte B entre los elegidos
   └─ verificar(...)             verificacion.py → lista de chequeos
        │
        ▼
 escribir(...)                   salida.json, traza.json, traza.md
        │
        ▼
 resumen.md  +  código de salida (0 si todo cumple, 1 si no)
```

La **medición de tiempo** usa `resolver` sin traza ni verificación: así el tiempo es el del algoritmo y no el de escribir la traza. La **traza** se obtiene en una ejecución aparte con las mismas entradas; como el algoritmo es determinista, produce las mismas decisiones.

### 3.3 Los datos: del JSON a las estructuras de Python

`cargar` convierte el JSON en un `Caso` (dataclass en `entrada.py`). Los nodos se identifican **por su posición** 0..N−1 en el archivo; los ids (`"N01"`) solo se usan para mostrar resultados.

| En el informe | En el código | Contenido |
|---|---|---|
| `N`, `k`, `B` | `caso.N`, `caso.k`, `caso.B` | enteros |
| `S_j` (categorías del nodo j) | `caso.S[j]` | `set` de textos, p. ej. `{"C11","C17","C19"}` |
| `w_i` (coeficiente de utilidad) | `caso.coef[i]` | `float` |
| `u_i` | `caso.utilidad` | especificación, p. ej. `{"tipo": "log"}` |
| id del nodo j | `caso.ids[j]` | `"N01"`, ... |

Se usa `set` para las categorías porque la operación central, «qué categorías de `S_j` aún no están cubiertas», es una resta de conjuntos (`S[j] - cubierto`) que cuesta `O(|S_j|)`.

### 3.4 Selección: `seleccion_voraz_traza` (`src/solucion.py`)

Implementa el Algoritmo 3 del informe. Sin las líneas de traza, el núcleo es:

```python
N = len(S)
A, en_A, cubierto = [], [False] * N, set()
for it in range(1, k + 1):                  # una vuelta por cada lugar del cupo
    mejor, mejor_delta = None, -1
    for j in range(N):
        if not en_A[j]:                     # solo es candidato quien aún no está elegido
            delta = len(S[j] - cubierto)    # Δ_j: categorías de j que faltan por cubrir
            if delta > mejor_delta:         # '>' estricto: en empate gana el menor índice
                mejor, mejor_delta = j, delta
    A.append(mejor)
    en_A[mejor] = True
    cubierto |= S[mejor]                    # ahora esas categorías ya están cubiertas
return A, len(cubierto)                     # f(A) = categorías cubiertas
```

| Variable | Significado |
|---|---|
| `A` | nodos elegidos hasta ahora, en orden de elección |
| `en_A[j]` | `True` si el nodo j ya está en `A` (consulta en `O(1)`) |
| `cubierto` | unión de las categorías de los nodos de `A`; su tamaño es `f(A)` |
| `delta` | ganancia marginal `Δ_j = f(A ∪ {j}) − f(A)` |

Por qué `len(S[j] - cubierto)` es la ganancia marginal: `f(A ∪ {j}) − f(A)` es la cantidad de categorías que `j` agrega, y esas son exactamente las de `S[j]` que no están en `cubierto`.

**Ejemplo con el caso incluido.** Iteración 1, con `cubierto` vacío, el Δ de cada nodo es simplemente `|S_j|`. Cuatro nodos empatan con 7: N03, N10, N11 y N15. Como la comparación es `>` estricto, el primero que se recorre (N03) se queda y los demás no lo superan. N03 aporta C01, C02, C08, C10, C15, C16 y C18, y `cubierto` pasa a tener 7 categorías.

Iteración 2: ahora Δ cuenta solo lo que falta. N10 tiene 7 categorías pero C16 ya está cubierta, así que Δ = 6. N11 también tenía 7 y ahora solo aporta 4, porque C01, C08 y C16 ya estaban. Gana N10 con 6. Por eso un nodo con muchas categorías puede dejar de ser atractivo: lo que cuenta es lo que **aporta de nuevo**.

**Trazabilidad.** Si se pasa una lista `traza`, en cada iteración se guarda un diccionario con el Δ de **todos** los candidatos (`deltas`), el elegido, su Δ (`ganancia`), las categorías que aporta (`nuevas`) y `f(A)` acumulada. Esas líneas solo leen; no cambian ninguna decisión. Eso es lo que se imprime en la tabla de selección de `traza.md`.

**Costo.** Hay `k` vueltas, `N` candidatos por vuelta y cada resta de conjuntos cuesta `O(s)`, con `s = máx |S_j|`: **`O(k·N·s)`**.

### 3.5 Reparto: `reparto_voraz_traza` (`src/solucion.py`)

Implementa el Algoritmo 1 del informe: entrega el presupuesto **de una unidad en una unidad** al nodo elegido cuya siguiente unidad aporta más.

```python
u = construir(spec, w)                       # u(i, x): utilidad del nodo i con x unidades
g = lambda i, x: u(i, x + 1) - u(i, x)       # ganancia marginal de darle su unidad x+1
x = [0] * n                                  # unidades de cada nodo elegido
H = [(-g(i, 0), i) for i in range(n)]        # montículo con la 1.ª ganancia de cada nodo
heapq.heapify(H)
for paso in range(1, B + 1):                 # una vuelta por cada unidad de presupuesto
    neg, i = heapq.heappop(H)                # nodo con mayor ganancia (guardada con signo -)
    x[i] += 1                                # se le entrega una unidad
    heapq.heappush(H, (-g(i, x[i]), i))      # entra su siguiente ganancia, que es menor
return x
```

- **Por qué `-g`:** `heapq` de Python es un montículo de **mínimos**; al guardar la ganancia con signo negativo, `heappop` entrega la mayor ganancia.
- **Por qué la tupla `(-g, i)`:** si dos nodos empatan en ganancia, Python compara el segundo elemento y gana el de menor índice, como en la selección.
- **Por qué es óptimo:** cada `u_i` es cóncava, así que las ganancias de un mismo nodo solo bajan; tomar siempre la mayor disponible nunca se arrepiente (teorema de optimalidad del informe).
- **Por qué el montículo:** sacar el máximo cuesta `O(log k)` y no hay que revisar a todos los nodos en cada paso.

**Ejemplo con el caso incluido.** Los 5 elegidos son N03, N10, N08, N09 y N01, con `w` = 9.1, 12.4, 10.6, 9.9 y 8.5. Con `u = w·ln(1+x)`, la primera unidad de cada uno vale `w·ln 2`: 8.595 para N10, 7.347 para N08, 6.862 para N09, 6.308 para N03 y 5.892 para N01. Los pasos 1 a 5 entregan una unidad a cada uno, de mayor a menor ganancia. Al dar la primera unidad a N10, su siguiente ganancia baja a 5.028 (`12.4·(ln 3 − ln 2)`). En el paso 6 esa ganancia sigue siendo la mayor disponible (la siguiente es 4.298, de N08), así que N10 recibe su segunda unidad. Al terminar las 30 unidades, el reparto es N03=5, N10=8, N08=6, N09=6, N01=5.

**Costo.** Construir el montículo cuesta `O(k)` y cada una de las `B` vueltas `O(log k)`: **`O(k + B·log k)`**. Es pseudo-polinomial: depende del **valor** de `B`.

### 3.6 Funciones de utilidad: `src/utilidades.py`

`u_i(x)` no está escrita dentro del algoritmo: el reparto la recibe como una función `u(i, x)`.

```python
def _saturacion(w, spec):
    return lambda i, x: w[i] * x / (1 + x)

FUNCIONES = {"log": _log, "sqrt": _sqrt, "saturacion": _saturacion, "potencia": _potencia}
```

- Cada tipo es una **fábrica**: recibe los coeficientes `w` y devuelve la función `u(i, x)`, que cuesta `O(1)` por llamada.
- `validar(spec)` rechaza tipos desconocidos y, para `potencia`, exponentes fuera de (0, 1), porque con `p ≥ 1` la función dejaría de ser cóncava y el voraz ya no sería óptimo.
- `construir(spec, w)` valida y devuelve la función. `solucion.py` solo llama a `construir`, así que agregar una función nueva no toca el algoritmo.

### 3.7 Entrada y validación: `src/entrada.py`

`cargar(ruta, utilidad=None)` hace tres cosas, en este orden:

1. Lee el JSON y comprueba que existan `parametros` y `nodos`, y los tres parámetros obligatorios.
2. Valida los valores: `numero_nodos` igual a la cantidad de nodos, ids únicos, `1 ≤ k < N`, `B` entero ≥ 0, coeficientes > 0 y categorías presentes y no vacías.
3. Convierte las categorías a conjuntos y devuelve el `Caso`.

Todo error es un `ValueError` que **nombra el caso**; `main` lo atrapa y lo muestra como una línea, sin traceback. Las claves que no conoce (`grafo`, `numero_rondas`, costos...) se ignoran.

### 3.8 Verificación: `src/verificacion.py`

`verificar(...)` recibe el resultado y las trazas y devuelve una lista de chequeos `{nombre, esperado, obtenido, cumple}`. Hay dos clases:

- **Consistencia interna.** Por ejemplo, `f(A)` de la traza se compara con `f_cobertura(S, A)` recalculada desde cero, y las ganancias de la traza deben ser no crecientes.
- **Contraste con el informe.** Se ejecutan `algoritmos.seleccion_voraz` y `algoritmos.reparto_voraz` de `Informe/code/algoritmos.py` con las mismas entradas y se exige el mismo resultado. Es la evidencia automática de que el código entregado corresponde al algoritmo del informe.

La optimalidad del reparto se comprueba probando todas las transferencias de **una** unidad de un nodo a otro: si alguna mejorara la utilidad, el reparto no sería óptimo.

### 3.9 Ejecución y salida: `src/ejecutar_casos.py`

| Función | Qué hace |
|---|---|
| `main` | Interpreta los argumentos (`-r`, `-o`, `--utilidad`, `--exponente`), recorre los casos y escribe `resumen.md`. Termina con código 0 o 1. |
| `ejecutar_caso` | Orquesta un caso (diagrama de §3.2) y cambia los índices por ids para la salida. |
| `medir` | Ejecuta `resolver` `-r` veces y devuelve la mediana con `time.perf_counter`. |
| `escribir` | Escribe `salida.json` y `traza.json`, y llama a `traza_md`. |
| `traza_md` | Construye el Markdown legible de la traza. |
| `version` | Lee el archivo `VERSION` para estampar la versión en todas las salidas. |

### 3.10 Cómo modificar o ampliar

| Quiero... | Qué tocar |
|---|---|
| Otra utilidad `u_i(x)` | Agregar una fábrica a `FUNCIONES` y `DESCRIPCION` en `utilidades.py`. No se toca el algoritmo. |
| Otra definición de `f(A)` | Cambiar `f_cobertura` y la línea `delta = len(S[j] - cubierto)` de `seleccion_voraz_traza`; adaptar `nuevas` y `f_acumulada` de la traza. |
| Otro campo de entrada | Leerlo y validarlo en `cargar` y guardarlo en `Caso`. |
| Otro chequeo | Agregar un `cs.append(_chk(...))` en `verificar`. |
| Otro formato de salida | `escribir` y `traza_md`. |

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
- **Algoritmo exacto por fuerza bruta.** Para esta entrega el óptimo exacto de la selección (`seleccion_exacta_ref`) se calcula por fuerza bruta, probando los `C(N,k)` subconjuntos. En la próxima entrega se reemplazará por una solución con programación dinámica.
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
