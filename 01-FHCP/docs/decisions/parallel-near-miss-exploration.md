# Exploración paralela de grafos sin ciclo certificado

## Contexto

Arturo solicitó volver a evaluar los 12 grafos que otro equipo reportó
resueltos y nuestra evaluación dejó sin certificado, usando paralelismo y
30 segundos por intento. Prefiere ejecutar personalmente el comando.

## Elección

Preparar una evaluación exploratoria separada: seis familias sin cambiar
operadores ni parámetros, diez semillas nuevas (2001–2010), 30 segundos,
cuatro procesos con un hilo nativo y un núcleo físico por proceso. Se
guardan todos los intentos y se comprueban los ciclos independientemente.
Se usa un esquema propio `fhcp-parallel-exploration/1`; el plan serial
distribuido y las evidencias de evaluaciones anteriores quedan intactos.

El coordinador reserva antes de lanzar, audita y actualiza tablas por cada
corrida, y reanuda sin repetir primarios. Recursos, fuentes y entorno se
registran; la ejecución real la inicia Arturo desde su terminal.

## Consecuencias

La selección está informada por resultados externos y reutiliza grafos:
no es una muestra confirmatoria ni una comparación independiente. Las
semillas nuevas evitan repetir deliberadamente las mismas búsquedas con
un presupuesto menor; no garantizan éxitos. Los procesos comparten
recursos y sus tiempos deben analizarse como paralelos. No se mezclan
automáticamente estos resultados con el consolidado del informe.

[Protocolo, comandos y evidencia](../experiments/near-miss-parallel-exploration.md).
