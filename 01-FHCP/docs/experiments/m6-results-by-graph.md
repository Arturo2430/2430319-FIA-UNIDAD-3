# Resultados de M6 por grafo

Campaña `e390b61f-aae4-4248-ba71-4467920d7bac`: **1,044 ejecuciones completadas, cero ciclos certificados**. Estas tablas reúnen las nueve instancias de la campaña original; la nueva prueba exploratoria de graph2 queda separada.

**Cómo leerlas:** «Mejor costo» es el menor número de conexiones faltantes, incluido el cierre, entre los candidatos disponibles. Solo un ciclo validado cuenta como éxito. Un costo positivo no es una solución. «Sin candidato» indica que no se terminó una ruta completa; esos intentos siguen incluidos. La mediana mide tiempo de solver por intento, incluidos los que agotaron su presupuesto; no es tiempo hasta solución.

Los presupuestos y configuraciones varían entre fases; las tablas de comprobación y ajuste no son equivalentes a evaluación. Se conservan las incidencias de swap y alimentación documentadas en [el resumen original](../../experiments/results/e390b61f-aae4-4248-ba71-4467920d7bac/campaign-summary.md).

## graph1 — 66 vértices, 99 aristas

**Comprobación inicial:** 1 semilla(s). Presupuesto por intento: 20 evaluaciones o 5 segundos, lo que ocurra primero.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c1 | 1/1 | 0 | 58 | 0 | 0 | 0.007 |
| SA | sa-c1 | 1/1 | 0 | 60 | 0 | 0 | 0.009 |
| AS | as-c1 | 1/1 | 0 | 8 | 0 | 0 | 0.124 |
| ABC | abc-c1 | 1/1 | 0 | 58 | 0 | 0 | 0.007 |
| DE | de-c1 | 1/1 | 0 | 58 | 0 | 0 | 0.012 |
| PSO | pso-c1 | 1/1 | 0 | 58 | 0 | 0 | 0.014 |

**Verificación de reproducibilidad:** 1 semilla(s); dos ejecuciones por combinación para comprobar reproducibilidad. Presupuesto por intento: 100 evaluaciones.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c2 | 2/2 | 0 | 56 | 0 | 0 | 0.029 |
| SA | sa-c1 | 2/2 | 0 | 58 | 0 | 0 | 0.026 |
| AS | as-c2 | 2/2 | 0 | 5 | 0 | 0 | 0.604 |
| ABC | abc-c2 | 2/2 | 0 | 57 | 0 | 0 | 0.022 |
| DE | de-c2 | 2/2 | 0 | 58 | 0 | 0 | 0.051 |
| PSO | pso-c1 | 2/2 | 0 | 58 | 0 | 0 | 0.051 |

## graph2 — 70 vértices, 106 aristas

**Comprobación inicial:** 1 semilla(s). Presupuesto por intento: 20 evaluaciones o 5 segundos, lo que ocurra primero.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c1 | 1/1 | 0 | 64 | 0 | 0 | 0.007 |
| SA | sa-c1 | 1/1 | 0 | 66 | 0 | 0 | 0.008 |
| AS | as-c1 | 1/1 | 0 | 8 | 0 | 0 | 0.136 |
| ABC | abc-c1 | 1/1 | 0 | 64 | 0 | 0 | 0.007 |
| DE | de-c1 | 1/1 | 0 | 64 | 0 | 0 | 0.013 |
| PSO | pso-c1 | 1/1 | 0 | 64 | 0 | 0 | 0.013 |

## graph58 — 396 vértices, 595 aristas

**Ajuste de parámetros:** 5 semilla(s). Presupuesto por intento: 2,000 evaluaciones o 10 segundos, lo que ocurra primero.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c1 | 5/5 | 0 | 371 | 0 | 0 | 2.740 |
| GA | ga-c2 | 5/5 | 0 | 360 | 0 | 0 | 2.811 |
| SA | sa-c1 | 5/5 | 0 | 370 | 0 | 0 | 2.464 |
| SA | sa-c2 | 5/5 | 0 | 383 | 0 | 0 | 2.439 |
| AS | as-c1 | 5/5 | 0 | 112 | 0 | 0 | 10.000 |
| AS | as-c2 | 5/5 | 0 | 37 | 0 | 0 | 10.000 |
| ABC | abc-c1 | 5/5 | 0 | 384 | 0 | 0 | 2.093 |
| ABC | abc-c2 | 5/5 | 0 | 385 | 0 | 0 | 2.101 |
| DE | de-c1 | 5/5 | 0 | 384 | 0 | 0 | 6.432 |
| DE | de-c2 | 5/5 | 0 | 384 | 0 | 0 | 6.433 |
| PSO | pso-c1 | 5/5 | 0 | 382 | 0 | 0 | 6.385 |
| PSO | pso-c2 | 5/5 | 0 | 383 | 0 | 0 | 6.400 |

## graph268 — 1,644 vértices, 2,767 aristas

**Ajuste de parámetros:** 5 semilla(s). Presupuesto por intento: 2,000 evaluaciones o 10 segundos, lo que ocurra primero.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c1 | 5/5 | 0 | 1627 | 0 | 0 | 10.001 |
| GA | ga-c2 | 5/5 | 0 | 1621 | 0 | 0 | 10.001 |
| SA | sa-c1 | 5/5 | 0 | 1627 | 0 | 0 | 9.756 |
| SA | sa-c2 | 5/5 | 0 | 1629 | 0 | 0 | 9.685 |
| AS | as-c1 | 5/5 | 0 | 1046 | 0 | 0 | 10.000 |
| AS | as-c2 | 5/5 | 0 | 265 | 0 | 0 | 10.000 |
| ABC | abc-c1 | 5/5 | 0 | 1633 | 0 | 0 | 8.690 |
| ABC | abc-c2 | 5/5 | 0 | 1633 | 0 | 0 | 8.396 |
| DE | de-c1 | 5/5 | 0 | 1634 | 0 | 0 | 10.003 |
| DE | de-c2 | 5/5 | 0 | 1632 | 0 | 0 | 10.001 |
| PSO | pso-c1 | 5/5 | 0 | 1633 | 0 | 0 | 10.008 |
| PSO | pso-c2 | 5/5 | 0 | 1633 | 0 | 0 | 10.001 |

## graph48 — 338 vértices, 776 aristas

**Evaluación principal:** 30 semilla(s). Presupuesto por intento: 10,000 evaluaciones o 30 segundos, lo que ocurra primero.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c2 | 30/30 | 0 | 248 | 0 | 0 | 11.845 |
| SA | sa-c1 | 30/30 | 0 | 196 | 0 | 0 | 10.375 |
| AS | as-c2 | 30/30 | 0 | 29 | 0 | 0 | 30.000 |
| ABC | abc-c2 | 30/30 | 0 | 295 | 0 | 0 | 8.857 |
| DE | de-c2 | 30/30 | 0 | 321 | 0 | 0 | 26.820 |
| PSO | pso-c1 | 30/30 | 0 | 310 | 0 | 0 | 26.684 |

## graph175 — 1,014 vértices, 2,328 aristas

**Evaluación principal:** 30 semilla(s). Presupuesto por intento: 10,000 evaluaciones o 30 segundos, lo que ocurra primero.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c2 | 30/30 | 0 | 936 | 0 | 0 | 30.001 |
| SA | sa-c1 | 30/30 | 0 | 878 | 0 | 0 | 30.001 |
| AS | as-c2 | 30/30 | 0 | 121 | 0 | 0 | 30.000 |
| ABC | abc-c2 | 30/30 | 0 | 991 | 0 | 0 | 26.436 |
| DE | de-c2 | 30/30 | 0 | 995 | 0 | 0 | 30.002 |
| PSO | pso-c1 | 30/30 | 0 | 985 | 0 | 0 | 30.002 |

## graph74 — 462 vértices, 756 aristas

**Evaluación principal:** 30 semilla(s). Presupuesto por intento: 10,000 evaluaciones o 30 segundos, lo que ocurra primero.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c2 | 30/30 | 0 | 380 | 0 | 0 | 16.288 |
| SA | sa-c1 | 30/30 | 0 | 330 | 0 | 0 | 14.222 |
| AS | as-c2 | 30/30 | 0 | 63 | 0 | 0 | 30.000 |
| ABC | abc-c2 | 30/30 | 0 | 434 | 0 | 0 | 12.263 |
| DE | de-c2 | 30/30 | 0 | 447 | 0 | 0 | 30.001 |
| PSO | pso-c1 | 30/30 | 0 | 438 | 0 | 0 | 30.000 |

## graph479 — 2,772 vértices, 4,536 aristas

**Evaluación principal:** 30 semilla(s). Presupuesto por intento: 10,000 evaluaciones o 30 segundos, lo que ocurra primero.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c2 | 30/30 | 0 | 2742 | 0 | 0 | 30.001 |
| SA | sa-c1 | 30/30 | 0 | 2746 | 0 | 0 | 30.002 |
| AS | as-c2 | 30/30 | 0 | 508 | 0 | 0 | 30.000 |
| ABC | abc-c2 | 30/30 | 0 | 2760 | 0 | 0 | 30.003 |
| DE | de-c2 | 30/30 | 0 | 2759 | 0 | 0 | 30.010 |
| PSO | pso-c1 | 30/30 | 0 | 2758 | 0 | 0 | 30.005 |

## graph1001 — 9,528 vértices, 13,968 aristas

**Escala:** 30 semilla(s). Presupuesto por intento: 10,000 evaluaciones o 30 segundos, lo que ocurra primero.

| Algoritmo | Configuración | Completados | Éxitos certificados | Mejor costo | Sin candidato | Errores | Mediana (s) |
|---|---|---:|---:|---:|---:|---:|---:|
| GA | ga-c2 | 30/30 | 0 | 9508 | 0 | 0 | 30.005 |
| SA | sa-c1 | 30/30 | 0 | 9521 | 0 | 0 | 30.006 |
| AS | as-c2 | 30/30 | 0 | — | 30 | 0 | 30.000 |
| ABC | abc-c2 | 30/30 | 0 | 9516 | 0 | 0 | 30.010 |
| DE | de-c2 | 30/30 | 0 | 9516 | 0 | 0 | 30.040 |
| PSO | pso-c1 | 30/30 | 0 | 9517 | 0 | 0 | 30.040 |

## Procedencia

Generadas a partir de los análisis originales y sus RunRecord; se comprobaron los hashes SHA-256 de los 1,044 registros. Se conserva cada configuración de ajuste por separado para no mezclar sus cinco semillas. Los intentos de verificación se muestran como repeticiones de una misma semilla.

- Comprobación inicial: [análisis de intentos](../../experiments/results/3db63fd9-6545-4199-a1ea-cf74bdd50444/analyses/f6a27088-cca6-4343-92f6-7153592c3da6/attempts.json).
- Ajuste de parámetros: [análisis de intentos](../../experiments/results/ef9646e3-1985-47b6-8f58-6744b2f70810/analyses/6745c342-d037-406b-a34d-7f764bd03819/attempts.json).
- Evaluación principal: [análisis de intentos](../../experiments/results/67191556-cc8d-4612-9517-e9b4cd0a2340/analyses/d3dcccf3-160d-412a-8d57-f7a0e101ec93/attempts.json).
- Escala: [análisis de intentos](../../experiments/results/22560abf-18ec-4dab-87a9-8e1141f7ed05/analyses/2953975a-1886-4c9a-8e89-23c76c2355fd/attempts.json).
- Verificación de reproducibilidad: [análisis de intentos](../../experiments/results/311e6dd4-2d47-4775-833d-c2969771094c/analyses/350d6ba8-42e4-40db-8abb-8066ed9c5aac/attempts.json).
