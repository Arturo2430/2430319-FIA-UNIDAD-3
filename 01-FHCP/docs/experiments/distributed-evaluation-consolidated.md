# Evaluación distribuida FHCP: resultados consolidados

Se auditaron **8,806 intentos**, con **345 éxitos por intento**, **15 grafos
distintos certificados**, 8,449 agotamientos y 12 incidencias conservadas.
La tasa descriptiva es 3.92 %. Hay 149 grafos iniciados: 144 completos,
cinco parciales y 852 sin iniciar. Las 51,254 combinaciones pendientes
no se imputan como fallos. La expectativa aproximada de entrega era 20
grafos resueltos; la meta original de 60 permanece sin alcanzar.

Los grafos certificados son `graph2`, `graph6`, `graph10`, `graph14`,
`graph18`, `graph23`, `graph27`, `graph31`, `graph56`, `graph72`,
`graph79`, `graph90`, `graph96`, `graph134` y `graph150`.

La comparación balanceada usa 144 grafos, 1,440 intentos por familia.
ABC alcanza los 15 grafos y 116 éxitos; GA 10 grafos, DE 9, PSO 8,
SA 6 y AS 2. Los totales por familia se solapan entre grafos y no se suman
como cobertura distinta. Las incidencias permanecen en los denominadores.

## Condiciones y trazabilidad

Se conserva el plan 10×60, UUID `45f464ae-50be-441b-b7ff-a261fba5028e`,
código `19ac5eaa46fbacc5a034dae6d14befbf171928db`, semillas 1001–1010,
seis familias y hasta 60 s de solver por intento. Los cinco paquetes
identificados en `packages.json` superaron SHA-256, CRC e inventario.
`combine` comprobó snapshots, artefactos, identidad, parámetros, costo y
ciclo; las celdas coinciden exactamente con cada resumen original.
No hay combinaciones repetidas ni miembros ausentes.

Hay **7,563 intentos seriales y 1,243 paralelos**. Eder aporta ambos modos,
con un coordinador de hasta cuatro procesos en núcleos separados. Esa
concurrencia difiere del plan serial y se documenta como desviación de
recursos. Los tiempos conjuntos mezclan modos y equipos: son descriptivos,
no comparaciones de eficiencia ni factores de aceleración.
Se conservan 8,804 duraciones disponibles y dos interrupciones sin duración;
la suma de 510,361.334 s (141.767 h) corresponde a procesos, no a tiempo calendario.

Los cinco parciales son `graph104` (5/60), `graph153` (53/60),
`graph185` (17/60), `graph222` (48/60) y `graph227` (43/60).
Se mantienen tres incidencias de Arturo, seis de Zapata, dos de César
y una de Eder. No se lanzaron solvers para preparar esta documentación.

## Evidencia y comandos

[Tablas](../../experiments/results/team-evaluation-consolidated-20261117/tables.md) ·
[Totales](../../experiments/results/team-evaluation-consolidated-20261117/totals.json) ·
[Paquetes](../../experiments/results/team-evaluation-consolidated-20261117/packages.json) ·
[Modos por intento](../../experiments/results/team-evaluation-consolidated-20261117/execution-modes.csv) ·
[Comprobación de graph134](../../experiments/results/team-evaluation-consolidated-20261117/graph134-validation.json).

Para regenerar las tablas, elegir destinos vacíos:

```bash
python -m zipfile -e experiments/results/team-evaluation-consolidated-20261117/combined-evidence.zip /tmp/fhcp-consolidated-restored
python experiments/analysis/summarize_distributed_evaluation.py --combined /tmp/fhcp-consolidated-restored/combined --packages experiments/results/team-evaluation-consolidated-20261117/packages.json --output /tmp/fhcp-consolidated-tables
```

Para recertificar primarios se recupera un paquete por integrante desde
`packages.json`, se verifican sus hashes y se ejecuta `distributed_campaign combine`
con el plan congelado y los cinco directorios que contienen `machine.json`.
El archivo de procedencia identifica la transición de recursos de Eder;
los datos originales y sus fechas no se alteran. La campaña M6 se conserva
separada de esta evaluación y no se suman sus intentos a estos totales.
