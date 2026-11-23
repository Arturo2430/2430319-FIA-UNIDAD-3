# Prueba exploratoria

10 semillas; 10 s o 1,000,000 evaluaciones por intento. Instancias reutilizadas; separado de M6.

| Grafo | Algoritmo | Intentados/10 | Ciclos certificados/10 | Mejor costo | Mediana costo | Errores |
|---|---|---:|---:|---:|---:|---:|
| graph2 | ga | 10 | 2 | 0 | 1.0 | 0 |
| graph2 | sa | 10 | 0 | 1 | 2.0 | 0 |
| graph2 | as | 10 | 7 | 0 | 0.0 | 0 |
| graph2 | abc | 10 | 10 | 0 | 0.0 | 0 |
| graph2 | de | 10 | 2 | 0 | 1.0 | 0 |
| graph2 | pso | 10 | 0 | 1 | 1.0 | 0 |
| graph48 | ga | 10 | 0 | 7 | 8.5 | 0 |
| graph48 | sa | 10 | 0 | 9 | 12.0 | 0 |
| graph48 | as | 10 | 0 | 8 | 10.0 | 0 |
| graph48 | abc | 10 | 0 | 6 | 7.0 | 0 |
| graph48 | de | 10 | 0 | 7 | 9.0 | 0 |
| graph48 | pso | 10 | 0 | 7 | 9.0 | 0 |
| graph74 | ga | 10 | 0 | 8 | 11.0 | 0 |
| graph74 | sa | 10 | 0 | 14 | 19.0 | 0 |
| graph74 | as | 10 | 0 | 9 | 10.5 | 0 |
| graph74 | abc | 10 | 0 | 7 | 9.0 | 0 |
| graph74 | de | 10 | 0 | 8 | 11.5 | 0 |
| graph74 | pso | 10 | 0 | 10 | 12.0 | 0 |

Costo positivo: aristas faltantes, no prueba de imposibilidad. None: sin candidato disponible. Los tiempos CSV incluyen arranque del proceso y los intentos censurados; no son tiempos medios hasta resolver. Intentos no iniciados = 10 menos intentados. Los errores permanecen en el denominador previsto.
