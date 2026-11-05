# Traza del caso `entrada_G2_red_15_nodos` (versión 1.1.0)

N=15, rondas=3, k=5, B=30. u_i(x) = w_i*ln(1+x). Desempates: menor índice.

## Ronda 1

### 1. Selección de nodos (voraz por ganancia marginal Δ)

| Iter | Elegido | Δ del elegido | f(A) acumulada | Mejores 3 candidatos (nodo: Δ) |
|---|---|---|---|---|
| 1 | N11 | 10.5000 | 10.5000 | N11: 10.500, N09: 9.750, N07: 9.100 |
| 2 | N14 | 0.8500 | 11.3500 | N14: 0.850, N13: 0.800, N15: 0.800 |
| 3 | N15 | 0.7500 | 12.1000 | N15: 0.750, N12: 0.450, N13: 0.450 |
| 4 | N12 | 0.4500 | 12.5500 | N12: 0.450, N13: 0.450, N01: 0.200 |
| 5 | N13 | 0.4500 | 13.0000 | N13: 0.450, N01: 0.200, N02: 0.200 |

A = ['N11', 'N14', 'N15', 'N12', 'N13'],  f(A) = 13.0000  (óptimo exacto f* = 13.0000, razón 1.0000)

### 2. Reparto del presupuesto de ruido (una unidad por paso al mayor g_i(x))

| Paso | Nodo | Ganancia marginal g | x del nodo | Próxima ganancia del nodo |
|---|---|---|---|---|
| 1 | N12 | 8.1791 | 1 | 4.7845 |
| 2 | N14 | 7.0008 | 1 | 4.0952 |
| 3 | N15 | 6.5849 | 1 | 3.8519 |
| 4 | N13 | 5.7531 | 1 | 3.3654 |
| 5 | N11 | 5.2679 | 1 | 3.0815 |
| 6 | N12 | 4.7845 | 2 | 3.3946 |
| 7 | N14 | 4.0952 | 2 | 2.9056 |
| 8 | N15 | 3.8519 | 2 | 2.7330 |
| 9 | N12 | 3.3946 | 3 | 2.6331 |
| 10 | N13 | 3.3654 | 2 | 2.3878 |
| 11 | N11 | 3.0815 | 2 | 2.1864 |
| 12 | N14 | 2.9056 | 3 | 2.2537 |
| 13 | N15 | 2.7330 | 3 | 2.1199 |
| 14 | N12 | 2.6331 | 4 | 2.1514 |
| 15 | N13 | 2.3878 | 3 | 1.8521 |
| 16 | N14 | 2.2537 | 4 | 1.8414 |
| 17 | N11 | 2.1864 | 3 | 1.6959 |
| 18 | N12 | 2.1514 | 5 | 1.8190 |
| 19 | N15 | 2.1199 | 4 | 1.7321 |
| 20 | N13 | 1.8521 | 4 | 1.5133 |
| 21 | N14 | 1.8414 | 5 | 1.5569 |
| 22 | N12 | 1.8190 | 6 | 1.5757 |
| 23 | N15 | 1.7321 | 5 | 1.4644 |
| 24 | N11 | 1.6959 | 4 | 1.3856 |
| 25 | N12 | 1.5757 | 7 | 1.3898 |
| 26 | N14 | 1.5569 | 6 | 1.3487 |
| 27 | N13 | 1.5133 | 5 | 1.2795 |
| 28 | N15 | 1.4644 | 6 | 1.2685 |
| 29 | N12 | 1.3898 | 8 | 1.2433 |
| 30 | N11 | 1.3856 | 5 | 1.1715 |

Reparto final: N11=5, N14=6, N15=6, N12=8, N13=5  (suma = 30, utilidad = 92.5561)

### 3. Verificación de restricciones

| Restricción | Tipo | Esperado | Obtenido | Resultado |
|---|---|---|---|---|
| |A| = k | obligatoria | 5 | 5 | CUMPLE |
| nodos de A distintos y válidos | obligatoria | True | True | CUMPLE |
| f(A) de la traza = f(A) recalculada desde cero | obligatoria | 13.0 | 13.0 | CUMPLE |
| ganancias marginales de la selección no crecientes (submodularidad) | obligatoria | True | True | CUMPLE |
| sum(x) = B | obligatoria | 30 | 30 | CUMPLE |
| x_i entero >= 0 | obligatoria | True | True | CUMPLE |
| ganancias del reparto no crecientes (concavidad) | obligatoria | True | True | CUMPLE |
| reparto óptimo: ninguna transferencia de 1 unidad mejora la utilidad | obligatoria | <= 0 | 0.000e+00 | CUMPLE |
| garantía f(voraz) >= (1-1/e) f(óptimo) | obligatoria | >= 8.2176 | 13.0000 | CUMPLE |
| costo de participación de A <= presupuesto de costos (la base no lo impone) | informativa | <= 24 | 25 | **NO CUMPLE (informativa)** |
| consumo acumulado por nodo <= presupuesto_total_nodo (la base no lo impone) | informativa | sin excesos | sin excesos | CUMPLE |

## Ronda 2

### 1. Selección de nodos (voraz por ganancia marginal Δ)

| Iter | Elegido | Δ del elegido | f(A) acumulada | Mejores 3 candidatos (nodo: Δ) |
|---|---|---|---|---|
| 1 | N11 | 10.5000 | 10.5000 | N11: 10.500, N09: 9.750, N07: 9.100 |
| 2 | N14 | 0.8500 | 11.3500 | N14: 0.850, N13: 0.800, N15: 0.800 |
| 3 | N15 | 0.7500 | 12.1000 | N15: 0.750, N12: 0.450, N13: 0.450 |
| 4 | N12 | 0.4500 | 12.5500 | N12: 0.450, N13: 0.450, N01: 0.200 |
| 5 | N13 | 0.4500 | 13.0000 | N13: 0.450, N01: 0.200, N02: 0.200 |

A = ['N11', 'N14', 'N15', 'N12', 'N13'],  f(A) = 13.0000  (óptimo exacto f* = 13.0000, razón 1.0000)

### 2. Reparto del presupuesto de ruido (una unidad por paso al mayor g_i(x))

| Paso | Nodo | Ganancia marginal g | x del nodo | Próxima ganancia del nodo |
|---|---|---|---|---|
| 1 | N12 | 8.1791 | 1 | 4.7845 |
| 2 | N14 | 7.0008 | 1 | 4.0952 |
| 3 | N15 | 6.5849 | 1 | 3.8519 |
| 4 | N13 | 5.7531 | 1 | 3.3654 |
| 5 | N11 | 5.2679 | 1 | 3.0815 |
| 6 | N12 | 4.7845 | 2 | 3.3946 |
| 7 | N14 | 4.0952 | 2 | 2.9056 |
| 8 | N15 | 3.8519 | 2 | 2.7330 |
| 9 | N12 | 3.3946 | 3 | 2.6331 |
| 10 | N13 | 3.3654 | 2 | 2.3878 |
| 11 | N11 | 3.0815 | 2 | 2.1864 |
| 12 | N14 | 2.9056 | 3 | 2.2537 |
| 13 | N15 | 2.7330 | 3 | 2.1199 |
| 14 | N12 | 2.6331 | 4 | 2.1514 |
| 15 | N13 | 2.3878 | 3 | 1.8521 |
| 16 | N14 | 2.2537 | 4 | 1.8414 |
| 17 | N11 | 2.1864 | 3 | 1.6959 |
| 18 | N12 | 2.1514 | 5 | 1.8190 |
| 19 | N15 | 2.1199 | 4 | 1.7321 |
| 20 | N13 | 1.8521 | 4 | 1.5133 |
| 21 | N14 | 1.8414 | 5 | 1.5569 |
| 22 | N12 | 1.8190 | 6 | 1.5757 |
| 23 | N15 | 1.7321 | 5 | 1.4644 |
| 24 | N11 | 1.6959 | 4 | 1.3856 |
| 25 | N12 | 1.5757 | 7 | 1.3898 |
| 26 | N14 | 1.5569 | 6 | 1.3487 |
| 27 | N13 | 1.5133 | 5 | 1.2795 |
| 28 | N15 | 1.4644 | 6 | 1.2685 |
| 29 | N12 | 1.3898 | 8 | 1.2433 |
| 30 | N11 | 1.3856 | 5 | 1.1715 |

Reparto final: N11=5, N14=6, N15=6, N12=8, N13=5  (suma = 30, utilidad = 92.5561)

### 3. Verificación de restricciones

| Restricción | Tipo | Esperado | Obtenido | Resultado |
|---|---|---|---|---|
| |A| = k | obligatoria | 5 | 5 | CUMPLE |
| nodos de A distintos y válidos | obligatoria | True | True | CUMPLE |
| f(A) de la traza = f(A) recalculada desde cero | obligatoria | 13.0 | 13.0 | CUMPLE |
| ganancias marginales de la selección no crecientes (submodularidad) | obligatoria | True | True | CUMPLE |
| sum(x) = B | obligatoria | 30 | 30 | CUMPLE |
| x_i entero >= 0 | obligatoria | True | True | CUMPLE |
| ganancias del reparto no crecientes (concavidad) | obligatoria | True | True | CUMPLE |
| reparto óptimo: ninguna transferencia de 1 unidad mejora la utilidad | obligatoria | <= 0 | 0.000e+00 | CUMPLE |
| garantía f(voraz) >= (1-1/e) f(óptimo) | obligatoria | >= 8.2176 | 13.0000 | CUMPLE |
| costo de participación de A <= presupuesto de costos (la base no lo impone) | informativa | <= 24 | 25 | **NO CUMPLE (informativa)** |
| consumo acumulado por nodo <= presupuesto_total_nodo (la base no lo impone) | informativa | sin excesos | sin excesos | CUMPLE |

## Ronda 3

### 1. Selección de nodos (voraz por ganancia marginal Δ)

| Iter | Elegido | Δ del elegido | f(A) acumulada | Mejores 3 candidatos (nodo: Δ) |
|---|---|---|---|---|
| 1 | N11 | 10.5000 | 10.5000 | N11: 10.500, N09: 9.750, N07: 9.100 |
| 2 | N14 | 0.8500 | 11.3500 | N14: 0.850, N13: 0.800, N15: 0.800 |
| 3 | N15 | 0.7500 | 12.1000 | N15: 0.750, N12: 0.450, N13: 0.450 |
| 4 | N12 | 0.4500 | 12.5500 | N12: 0.450, N13: 0.450, N01: 0.200 |
| 5 | N13 | 0.4500 | 13.0000 | N13: 0.450, N01: 0.200, N02: 0.200 |

A = ['N11', 'N14', 'N15', 'N12', 'N13'],  f(A) = 13.0000  (óptimo exacto f* = 13.0000, razón 1.0000)

### 2. Reparto del presupuesto de ruido (una unidad por paso al mayor g_i(x))

| Paso | Nodo | Ganancia marginal g | x del nodo | Próxima ganancia del nodo |
|---|---|---|---|---|
| 1 | N12 | 8.1791 | 1 | 4.7845 |
| 2 | N14 | 7.0008 | 1 | 4.0952 |
| 3 | N15 | 6.5849 | 1 | 3.8519 |
| 4 | N13 | 5.7531 | 1 | 3.3654 |
| 5 | N11 | 5.2679 | 1 | 3.0815 |
| 6 | N12 | 4.7845 | 2 | 3.3946 |
| 7 | N14 | 4.0952 | 2 | 2.9056 |
| 8 | N15 | 3.8519 | 2 | 2.7330 |
| 9 | N12 | 3.3946 | 3 | 2.6331 |
| 10 | N13 | 3.3654 | 2 | 2.3878 |
| 11 | N11 | 3.0815 | 2 | 2.1864 |
| 12 | N14 | 2.9056 | 3 | 2.2537 |
| 13 | N15 | 2.7330 | 3 | 2.1199 |
| 14 | N12 | 2.6331 | 4 | 2.1514 |
| 15 | N13 | 2.3878 | 3 | 1.8521 |
| 16 | N14 | 2.2537 | 4 | 1.8414 |
| 17 | N11 | 2.1864 | 3 | 1.6959 |
| 18 | N12 | 2.1514 | 5 | 1.8190 |
| 19 | N15 | 2.1199 | 4 | 1.7321 |
| 20 | N13 | 1.8521 | 4 | 1.5133 |
| 21 | N14 | 1.8414 | 5 | 1.5569 |
| 22 | N12 | 1.8190 | 6 | 1.5757 |
| 23 | N15 | 1.7321 | 5 | 1.4644 |
| 24 | N11 | 1.6959 | 4 | 1.3856 |
| 25 | N12 | 1.5757 | 7 | 1.3898 |
| 26 | N14 | 1.5569 | 6 | 1.3487 |
| 27 | N13 | 1.5133 | 5 | 1.2795 |
| 28 | N15 | 1.4644 | 6 | 1.2685 |
| 29 | N12 | 1.3898 | 8 | 1.2433 |
| 30 | N11 | 1.3856 | 5 | 1.1715 |

Reparto final: N11=5, N14=6, N15=6, N12=8, N13=5  (suma = 30, utilidad = 92.5561)

### 3. Verificación de restricciones

| Restricción | Tipo | Esperado | Obtenido | Resultado |
|---|---|---|---|---|
| |A| = k | obligatoria | 5 | 5 | CUMPLE |
| nodos de A distintos y válidos | obligatoria | True | True | CUMPLE |
| f(A) de la traza = f(A) recalculada desde cero | obligatoria | 13.0 | 13.0 | CUMPLE |
| ganancias marginales de la selección no crecientes (submodularidad) | obligatoria | True | True | CUMPLE |
| sum(x) = B | obligatoria | 30 | 30 | CUMPLE |
| x_i entero >= 0 | obligatoria | True | True | CUMPLE |
| ganancias del reparto no crecientes (concavidad) | obligatoria | True | True | CUMPLE |
| reparto óptimo: ninguna transferencia de 1 unidad mejora la utilidad | obligatoria | <= 0 | 0.000e+00 | CUMPLE |
| garantía f(voraz) >= (1-1/e) f(óptimo) | obligatoria | >= 8.2176 | 13.0000 | CUMPLE |
| costo de participación de A <= presupuesto de costos (la base no lo impone) | informativa | <= 24 | 25 | **NO CUMPLE (informativa)** |
| consumo acumulado por nodo <= presupuesto_total_nodo (la base no lo impone) | informativa | sin excesos | excede: N12 | **NO CUMPLE (informativa)** |
