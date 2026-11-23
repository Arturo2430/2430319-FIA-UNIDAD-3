# Prueba exploratoria paralela de 12 grafos

Responsable: Junior Arturo Vázquez Leonel · @Arturo2430.
Preparación: 17 de noviembre de 2026. No iniciada durante la preparación.

Se seleccionaron `graph1`, `graph4`, `graph8`, `graph35`, `graph39`,
`graph43`, `graph47`, `graph52`, `graph67`, `graph78`, `graph85` y `graph99`:
el otro equipo reportó éxitos y nuestro consolidado no tenía ciclos en ellos.
Los CSV externos son conteos reportados, sin rutas recertificadas aquí.
Se trata de selección exploratoria y reutilización de instancias.

- GA, SA, AS, ABC, DE y PSO, con los parámetros mejorados de la evaluación.
- Diez semillas nuevas, 2001–2010: 60 corridas por grafo y 720 en total.
- Hasta 30 segundos de solver, incluida inicialización y validación; sin
  límite de evaluaciones o iteraciones. Termina antes al certificar ciclo.
- Cuatro procesos independientes, un hilo nativo por proceso, afinidad a
  cuatro núcleos físicos distintos. Máximo una corrida activa por grafo.
- Hasta 90 segundos externos por proceso, incluidos carga y arranque.
- No se detiene un grafo al primer éxito: conserva todas sus combinaciones.
- Hasta seis horas agregadas de presupuesto de solver; con cuatro procesos,
  unas 1½–2 horas de pared estimadas, según éxitos, carga y sobrecarga.

El [plan](../../experiments/configs/near-miss-12-parallel-10x30.json) tiene un
UUID y un esquema exploratorio propios; no cambia el plan distribuido serial.
El [catálogo seleccionado](../../experiments/configs/near-miss-12-catalog.json)
conserva exactamente los grafos originales y sus hashes. El código de solver
se conserva en `19ac5eaa46fbacc5a034dae6d14befbf171928db` y se verifica por
hash antes de iniciar y durante la sesión. Los resultados no se suman
automáticamente a los 15 grafos certificados del reporte.

## Comandos en esta laptop Linux

Desde la raíz del proyecto, comprobar sin lanzar algoritmos:

```bash
.venv/bin/python scripts/run_parallel_exploration.py --check
```

Ejecutar conectado a corriente, con al menos 4 GiB disponibles:

```bash
systemd-inhibit --what=sleep:idle --mode=block --why="Prueba FHCP paralela" .venv/bin/python -u scripts/run_parallel_exploration.py
```

El comando evita suspensión por inactividad mientras está abierto. Mantener
la terminal y la tapa abiertas; no apagar ni suspender manualmente.
El ejecutador pausa nuevas admisiones si se desconecta la corriente,
queda poca RAM o disco, o cambia el código fuente. No modifica swap ni
ajustes persistentes de energía. Las sesiones seriales del mismo entorno
quedan excluidas mediante el bloqueo de campaña compartido.

`Ctrl+C` detiene nuevas admisiones y conserva las reservas y auditorías;
los hijos activos pueden quedar interrumpidos y se registran como incidencias.
Repetir el mismo comando reanuda únicamente los pendientes: no repite los
éxitos, agotamientos ni errores ya admitidos. Código 3 significa pausa con
pendientes; código 0, cobertura conciliada, incluso si hubo incidencias.
No significa que los 12 grafos estén resueltos.

Para una pausa sin enviar señales a los hijos, crear un archivo vacío
llamado `STOP` dentro de la carpeta de resultados. El coordinador deja
finalizar los activos. Retirar solo ese archivo antes de reanudar.
`--max-attempts N` permite admitir N intentos nuevos y luego pausar.

## Resultados y evidencia

Carpeta fija para este plan:

`experiments/results/near-miss-12-8d8c7fdd-0754-4515-ab98-e14548c63ae6/`

Conserva `plan.json`, `machine.json`, snapshot de fuentes, copia del
coordinador y `terminal.log`; por intento guarda intención, parámetros,
semilla, stdout con ruta candidata, stderr, salida, identidad de proceso
y auditoría independiente. `summary.json`, `summary.csv` y `summary.md`
se actualizan después de cada corrida terminada y al cerrar la sesión.
El historial queda en `sessions/`. No sobrescribe las entregas anteriores.

Los ciclos se recertifican contra las instancias originales y se exige
certificado dentro del presupuesto. Agotamientos e interrupciones se
conservan. Los tiempos describen este modo paralelo; no equivalen a una
comparación serial controlada ni acreditan aceleración.

## Comprobaciones de preparación

Se ejecutaron `--check`, las tres pruebas del coordinador paralelo y las
48 del ejecutador distribuido: **51 aprobadas**. Se comprobó el inventario
de los 12 grafos, entorno, parámetros, 720 claves únicas y cuatro núcleos
físicos disponibles (CPUs 0, 2, 4 y 6 en esta laptop). No se ejecutaron los
algoritmos de esta prueba durante la preparación.
