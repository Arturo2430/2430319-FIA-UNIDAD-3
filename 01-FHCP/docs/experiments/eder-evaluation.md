# Evaluación experimental FHCP de Eder

**Responsable:** Eder Omar Zúñiga Zavala · @KirbyStone69.
**Asignación:** [#86](https://github.com/ZapataFrame/FHCP-Challenge/issues/86).
**Evidencia:** [carpeta Eder en Drive](https://drive.google.com/drive/folders/1GO8g4-chyUJnl6u7ah-2Bjfq6mdfAd3A).

## Resultados consolidados

| Métrica | Resultado |
| --- | ---: |
| Intentos auditados | 2,611 de 11,700 |
| Grafos con 60 combinaciones conciliadas | 42 |
| Grafos parciales | 2 |
| Grafos distintos certificados | 4 |
| Éxitos por intento | 98 |
| Agotamientos | 2,512 |
| Incidencias conservadas | 1 |
| Combinaciones pendientes | 9,089 |

| Grafo | GA | SA | AS | ABC | DE | PSO | Éxitos/60 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| graph14 | 0 | 0 | 0 | 9 | 0 | 0 | 9 |
| graph56 | 0 | 0 | 0 | 1 | 0 | 0 | 1 |
| graph79 | 10 | 3 | 0 | 10 | 10 | 10 | 43 |
| graph134 | 10 | 5 | 0 | 10 | 10 | 10 | 45 |

`graph134` tiene 724 vértices y 131,045 aristas. Se comprobaron sus 45
ciclos contra las aristas originales, verificando permutación, cada arista
consecutiva y cierre. Los éxitos repetidos cuentan como un solo grafo.
Los dos parciales son `graph222` (48/60) y `graph227` (43/60).
La incidencia de `graph74`/GA/1007 se conserva y no se reintenta.

## Protocolo y recursos

Commit `19ac5eaa46fbacc5a034dae6d14befbf171928db`; plan
`45f464ae-50be-441b-b7ff-a261fba5028e`, digest
`348df5525871354ff25a60b22ccb8da8d6aba9884de9a3a9b4026feafc0db250`.
Seis familias, semillas 1001–1010, 60 s por solver y 120 s externos,
sin límite de iteraciones o evaluaciones. AMD Ryzen 5 4600G,
21.31 GiB de RAM, Debian 13, CPython 3.14.10 con GIL y NumPy 2.5.4.

El paquete contiene 1,368 intentos secuenciales y 1,243 bajo un coordinador
de hasta cuatro procesos en núcleos distintos. La concurrencia difiere del
plan serial y se registra como desviación de recursos. Los hashes del solver,
parámetros y presupuesto individual coinciden con el plan congelado.
Los tiempos paralelos no se presentan como equivalentes a mediciones seriales.
La suma de 151,762.105 s es tiempo agregado de procesos, no duración calendario.

## Integridad y reproducción

[ZIP auditado](https://drive.google.com/file/d/14q6Tdwm8rX3w20HKulp93831LAaizxEj/view):
16,648,217 bytes, 15,738 entradas, CRC correcto, sin rutas inseguras,
enlaces simbólicos ni nombres repetidos. SHA-256:
`b380da5bd291a9623b97bc486a53bc4add13c872d094cbdb8a837c25b54f7f5a`.

El agregador oficial recertificó los 2,611 intentos y reprodujo exactamente
las celdas del `summary.json` del paquete. La consolidación usa un solo
paquete acumulado por integrante, sin sumar dos veces intentos repetidos.

[Consolidado del equipo](distributed-evaluation-consolidated.md),
[tablas por grafo](../../experiments/results/team-evaluation-consolidated-20261117/tables.md),
[comprobación independiente de graph134](../../experiments/results/team-evaluation-consolidated-20261117/graph134-validation.json)
y [procedencia de recursos](../../experiments/results/team-evaluation-consolidated-20261117/execution-provenance.json).
Los registros de sesiones se conservan en [su archivo de procedencia](eder-evaluation-sessions.md).
