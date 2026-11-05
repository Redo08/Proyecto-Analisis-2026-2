# Manual técnico — Solución base del Subproyecto 2 (versión 1.1.0)

Contenido: 1. Problema · 2. Algoritmos · 3. Estructura del código · 4. Formato de entrada · 5. Formato de salida y traza · 6. Pasos de ejecución · 7. Verificación de restricciones · 8. Limitaciones · 9. Correspondencia con el informe

## 1. Problema

En cada ronda de aprendizaje colaborativo hay dos decisiones:

1. **Selección (Parte 2).** Elegir un grupo `A` de `k` nodos entre `N` candidatos que maximice la utilidad conjunta `f(A)`. Es NP-difícil (el informe lo demuestra por reducción desde Max-Cover).
2. **Reparto (Parte 1).** Repartir `B` unidades enteras de presupuesto de ruido entre los nodos de `A` para maximizar `Σ u_i(x_i)`, con `u_i` creciente y cóncava. Se resuelve de forma exacta en tiempo polinomial.

## 2. Algoritmos

### 2.1 Selección voraz (Algoritmo 3 del informe)

```
A ← ∅
repetir k veces:
    para cada j ∉ A:  Δ_j(A) = f(A ∪ {j}) − f(A)      # ganancia marginal
    agregar a A el j con mayor Δ_j(A)                  # empate → menor índice
```

Garantía: `f(A) ≥ (1 − 1/e) · f(óptimo)` si `f` es monótona y submodular.

**Utilidad conjunta usada con el grafo de los casos.** Sea `P[j][v]` el peso de influencia entre `j` y `v` (grafo no dirigido) y `P[v][v] = 1`:

```
f(A) = Σ_v  max_{j ∈ A} P[j][v]
```

Cada nodo `v` queda «cubierto» en la medida de la mejor influencia que recibe de `A`. Es monótona y submodular (cobertura ponderada, tipo localización de instalaciones). Con pesos 0/1 coincide con la cobertura `|∪ S_j|` del informe, con `S_j` la vecindad cerrada de `j`.
Se mantiene `cob[v] = max_{j∈A} P[j][v]`, de modo que `Δ_j(A) = Σ_v max(0, P[j][v] − cob[v])`.

Costo: `k·N` evaluaciones de `Δ`, cada una `O(N)` → **`O(k·N²)`** para esta `f`.

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

### 2.3 Rondas

Se ejecuta `numero_rondas` veces el par selección + reparto. La solución base no tiene dinámica entre rondas (no hay fallas ni estado), así que las rondas son idénticas; se repiten para poder verificar el consumo acumulado por nodo.

## 3. Estructura del código

| Archivo | Responsabilidad |
|---|---|
| `src/entrada.py` | Lee y valida el JSON; construye `Caso` con la matriz `P`. Lanza `ValueError` con mensaje claro si algo es inválido. |
| `src/utilidades.py` | Catálogo y validación de las funciones `u_i(x)`. |
| `src/solucion.py` | `seleccion_voraz_traza`, `reparto_voraz_traza`, `seleccion_exacta_ref` (fuerza bruta de referencia si `C(N,k) ≤ 2·10⁶`) y `resolver_ronda`. Con `traza=None` no registra nada: las decisiones son las mismas con o sin traza. |
| `src/verificacion.py` | Chequeos de restricciones por ronda (§7). |
| `src/ejecutar_casos.py` | Programa principal: recorre casos, mide tiempo, escribe `resultados/`. |
| `Informe/code/algoritmos.py` | Implementación del informe. `solucion.py` repite sus pasos y añade la traza; con `log` el reparto es el mismo. |

La lógica del algoritmo no se edita para ejecutar un caso: todo cambio de datos se hace en el JSON y todo cambio de salida en las opciones de la línea de comandos.

## 4. Formato de entrada (JSON)

```json
{
  "parametros": {
    "numero_nodos": 15,                         // debe ser igual a len(nodos)
    "numero_rondas": 3,                         // entero >= 1
    "cupo_participantes_por_ronda_k": 5,        // entero, 1 <= k < N
    "presupuesto_ruido_por_ronda_B": 30,        // entero >= 0
    "presupuesto_costos_participacion_por_ronda": 24   // opcional; solo se verifica
  },
  "funcion_utilidad": {"tipo": "log"},          // opcional; ver §2.2 (log, sqrt, saturacion, potencia)
  "grafo": [ {"u": "N01", "v": "N02", "peso_influencia": 0.25}, ... ],   // aristas no dirigidas, peso en [0,1]
  "nodos": [ {"id": "N01", "coeficiente_utilidad": 8.5,                   // > 0 (es w_i)
              "presupuesto_total_nodo": 18,                               // opcional; solo se verifica
              "costo_participacion": 3}, ... ]                            // opcional; solo se verifica
}
```

Las aristas no listadas se toman con influencia 0. Ids repetidos, aristas a nodos inexistentes, lazos, pesos fuera de [0,1] o `k ≥ N` se rechazan con un error explicativo.
El nombre del caso es el nombre del archivo sin `.json`.

## 5. Formato de salida y traza

Por caso, en `resultados/<caso>/`:

| Archivo | Contenido |
|---|---|
| `salida.json` | versión, parámetros, entorno (Python/SO), **tiempo** (mediana por ronda, repeticiones, todas las mediciones), óptimo exacto de referencia, bandera `restricciones_obligatorias_ok`, y por ronda: selección, `f(A)`, reparto, utilidad, costo de participación y verificación. |
| `traza.md` | Traza legible, por ronda: **(1)** tabla de selección con elegido, Δ, `f(A)` acumulada y 3 mejores candidatos; **(2)** tabla de reparto, una fila por unidad de presupuesto con nodo, ganancia marginal, `x` del nodo y siguiente ganancia; **(3)** tabla de verificación de restricciones. |
| `traza.json` | La misma traza completa en formato máquina (en selección, Δ de **todos** los candidatos en cada iteración). |

Además, `resultados/resumen.md` tiene una fila por caso: N, k, B, tiempo por ronda, `f(A)`, óptimo, estado de restricciones.

**Tiempo.** Mediana de `-r` repeticiones (por defecto 5) de **una ronda sin traza** con `time.perf_counter`. `salida.json` también da `total_rondas_s` (= mediana × rondas). El tiempo de carga del archivo, de la referencia exacta y de la verificación no se incluye. Los tiempos varían de una máquina a otra; las decisiones no.

## 6. Pasos de ejecución

```bash
git clone <repositorio> && cd RepoProyecto
python --version                              # 3.10 o superior
python src/ejecutar_casos.py                  # genera resultados/
```

No se requieren dependencias para estos pasos (solo biblioteca estándar).

Código de salida: `0` si las restricciones **obligatorias** se cumplen en todos los casos; `1` si alguna falla. Para casos de la profesora: copiar sus `.json` a `casos/` y ejecutar el mismo comando; para uno solo, `python src/ejecutar_casos.py ruta/al/caso.json`.
Con otra utilidad: `python src/ejecutar_casos.py --utilidad saturacion -o resultados_saturacion`.
Para regenerar gráficas y tablas del informe (opcional): `pip install -r requirements.txt` y `python Informe/code/experimentos.py`.

## 7. Verificación de restricciones

**Obligatorias** (las impone la solución base; si fallan, el código de salida es 1):

| Chequeo | Qué comprueba |
|---|---|
| `\|A\| = k`, nodos distintos y válidos | Selección bien formada |
| `f(A)` de la traza = `f(A)` recalculada desde cero | La acumulación incremental es correcta |
| Ganancias de la selección no crecientes | Consecuencia de la submodularidad |
| `Σ x = B`, `x_i` entero ≥ 0 | Reparto factible |
| Ganancias del reparto no crecientes | Concavidad observada |
| Ninguna transferencia de 1 unidad mejora | Optimalidad local del reparto (equivale a optimalidad global por concavidad) |
| `f(voraz) ≥ (1−1/e)·f(óptimo)` | Solo si se pudo calcular el óptimo exacto |

**Informativas** (el enunciado las pide, pero la solución base **no** las impone; se reportan sin afectar el código de salida): costo de participación de `A` ≤ `presupuesto_costos_participacion_por_ronda`, y consumo acumulado de cada nodo ≤ `presupuesto_total_nodo`.

## 8. Limitaciones

- **Costos de participación no impuestos.** La selección solo respeta el cupo `k`. En el caso de 15 nodos la selección cuesta 25 frente a un presupuesto de 24, así que **no es factible** para esa restricción. Con costos la cota del voraz cambia (Khuller et al., 1999); el informe lo deja como trabajo pendiente.
- **Presupuesto por nodo no impuesto.** N12 recibe 8 unidades por ronda, 24 en 3 rondas, frente a un total de 18.
- **Rondas sin dinámica.** No hay fallas de nodos ni cambios entre rondas; el resultado se repite.
- **Modelo de `f` y de `u_i` asumidos.** La `f` de influencia (§2.1) y la elección por defecto de `u_i` (`log`) son decisiones de modelado de este grupo, no vienen dadas en el archivo. Si la profesora define otra, hay que cambiar `f_total` y `seleccion_voraz_traza`; el resto no cambia. `f` no usa `coeficiente_utilidad` y los desempates dependen del orden de los nodos en el archivo (en este caso muchos nodos empatan en Δ).
- **Grafo no dirigido.** Si una arista aparece en ambos sentidos con pesos distintos, vale la última.
- **Escala.** `O(k·N²)` en selección con matriz densa `N×N` en memoria; adecuado para cientos de nodos, no para redes muy grandes. La fuerza bruta de referencia se omite si `C(N,k) > 2·10⁶`.
- **Precisión.** Utilidades en `float`; las comparaciones usan tolerancia `1e-9`. `B` se trata como entero pequeño (el reparto es `O(B log k)`).
- **Tiempos** de una sola máquina, con ruido del sistema operativo; con casos de milisegundos la desviación relativa es grande.

## 9. Correspondencia con el informe

| Informe | Código |
|---|---|
| Algoritmo 1, reparto voraz | `reparto_voraz_traza` (`Informe/code/algoritmos.py: reparto_voraz`) |
| Algoritmo 2, selección exacta | `seleccion_exacta_ref` (por combinaciones) |
| Algoritmo 3, selección voraz | `seleccion_voraz_traza` (`Informe/code/algoritmos.py: seleccion_voraz`) |
| Variantes (costos, rondas con fallas, nodos relacionados) | Pendiente; ver §8 |
