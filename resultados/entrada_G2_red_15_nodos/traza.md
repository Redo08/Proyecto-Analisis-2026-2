# Traza del caso `entrada_G2_red_15_nodos` (versión 1.1.0)

N=15, k=5, B=30. u_i(x) = w_i*ln(1+x). Desempates: menor índice.

## 1. Selección de nodos (voraz por ganancia marginal Δ)

Δ de un candidato = cuántas categorías **nuevas** aporta, es decir, las que su conjunto tiene y aún no cubren los ya elegidos. Se recalcula en cada iteración (por eso un nodo con Δ alto al inicio puede aportar poco después). La última columna sigue al mejor candidato descartado en la iteración anterior.

| Iter | Elegido | Δ | Categorías nuevas | f(A) acumulada | Mejores 3 candidatos (nodo: Δ) | Mejor descartado antes (Δ antes → Δ ahora) |
|---|---|---|---|---|---|---|
| 1 | N03 | 7 | C01, C02, C08, C10, C15, C16, C18 | 7 | N03: 7, N10: 7, N11: 7 | — |
| 2 | N10 | 6 | C07, C09, C13, C14, C17, C20 | 13 | N10: 6, N06: 5, N09: 5 | N10 (7 → 6) |
| 3 | N08 | 4 | C05, C06, C12, C19 | 17 | N08: 4, N06: 3, N13: 3 | N06 (5 → 3) |
| 4 | N09 | 2 | C03, C04 | 19 | N09: 2, N13: 2, N01: 1 | N06 (3 → 1) |
| 5 | N01 | 1 | C11 | 20 | N01: 1, N05: 1, N13: 1 | N13 (2 → 1) |

A = ['N03', 'N10', 'N08', 'N09', 'N01'],  f(A) = 20  (óptimo exacto f* = 20, razón 1.0000)

## 2. Reparto del presupuesto de ruido (una unidad por paso al mayor g_i(x))

| Paso | Nodo | Ganancia marginal g | x del nodo | Próxima ganancia del nodo |
|---|---|---|---|---|
| 1 | N10 | 8.5950 | 1 | 5.0278 |
| 2 | N08 | 7.3474 | 1 | 4.2979 |
| 3 | N09 | 6.8622 | 1 | 4.0141 |
| 4 | N03 | 6.3076 | 1 | 3.6897 |
| 5 | N01 | 5.8918 | 1 | 3.4465 |
| 6 | N10 | 5.0278 | 2 | 3.5673 |
| 7 | N08 | 4.2979 | 2 | 3.0494 |
| 8 | N09 | 4.0141 | 2 | 2.8481 |
| 9 | N03 | 3.6897 | 2 | 2.6179 |
| 10 | N10 | 3.5673 | 3 | 2.7670 |
| 11 | N01 | 3.4465 | 2 | 2.4453 |
| 12 | N08 | 3.0494 | 3 | 2.3653 |
| 13 | N09 | 2.8481 | 3 | 2.2091 |
| 14 | N10 | 2.7670 | 4 | 2.2608 |
| 15 | N03 | 2.6179 | 3 | 2.0306 |
| 16 | N01 | 2.4453 | 3 | 1.8967 |
| 17 | N08 | 2.3653 | 4 | 1.9326 |
| 18 | N10 | 2.2608 | 5 | 1.9115 |
| 19 | N09 | 2.2091 | 4 | 1.8050 |
| 20 | N03 | 2.0306 | 4 | 1.6591 |
| 21 | N08 | 1.9326 | 5 | 1.6340 |
| 22 | N10 | 1.9115 | 6 | 1.6558 |
| 23 | N01 | 1.8967 | 4 | 1.5497 |
| 24 | N09 | 1.8050 | 5 | 1.5261 |
| 25 | N03 | 1.6591 | 5 | 1.4028 |
| 26 | N10 | 1.6558 | 7 | 1.4605 |
| 27 | N08 | 1.6340 | 6 | 1.4154 |
| 28 | N01 | 1.5497 | 5 | 1.3103 |
| 29 | N09 | 1.5261 | 6 | 1.3220 |
| 30 | N10 | 1.4605 | 8 | 1.3065 |

Reparto final: N03=5, N10=8, N08=6, N09=6, N01=5  (suma = 30, utilidad = 98.6717)

## 3. Verificación de restricciones

| Restricción | Esperado | Obtenido | Resultado |
|---|---|---|---|
| tamaño de A = k | 5 | 5 | CUMPLE |
| nodos de A distintos y válidos | True | True | CUMPLE |
| f(A) de la traza = f(A) recalculada desde cero | 20 | 20 | CUMPLE |
| ganancias marginales de la selección no crecientes (submodularidad) | True | True | CUMPLE |
| selección idéntica a la implementación del informe (algoritmos.py) | [2, 9, 7, 8, 0] | [2, 9, 7, 8, 0] | CUMPLE |
| sum(x) = B | 30 | 30 | CUMPLE |
| x_i entero >= 0 | True | True | CUMPLE |
| ganancias del reparto no crecientes (concavidad) | True | True | CUMPLE |
| reparto idéntico a la implementación del informe (algoritmos.py) | [5, 8, 6, 6, 5] | [5, 8, 6, 6, 5] | CUMPLE |
| reparto óptimo: ninguna transferencia de 1 unidad mejora la utilidad | <= 0 | 0.000e+00 | CUMPLE |
| garantía f(voraz) >= (1-1/e) f(óptimo) | >= 12.6424 | 20 | CUMPLE |
