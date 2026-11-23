# Evaluación experimental FHCP: responsables y entregas

Cada issue contiene su lista exacta de grafos, instalación desde un checkout
nuevo, comandos Linux/PowerShell, sesiones de 60 minutos y reanudación. La
versión congelada es `2ee91991f111ca60ef7597f5cd3d957ac936d8b3` de la
[PR #82](https://github.com/ZapataFrame/FHCP-Challenge/pull/82), verificada en
[CI Linux y Windows](https://github.com/ZapataFrame/FHCP-Challenge/actions/runs/43566640381).
No actualizar código ni regenerar el plan durante las evaluaciones.

| Responsable | Issue | Grafos candidatos | Instrucciones conservadas | Carpeta final en Drive |
|---|---|---:|---|---|
| Junior Arturo Vázquez Leonel · @Arturo2430 | [#83](https://github.com/ZapataFrame/FHCP-Challenge/issues/83) | 220 | [Arturo2430.md](Arturo2430.md) | [Arturo](https://drive.google.com/drive/folders/1C7I1EFX8XKfGWad7hfwDaBPZybBsqSKZ) |
| Diego Eduardo Zapata Aguilar · @ZapataFrame | [#84](https://github.com/ZapataFrame/FHCP-Challenge/issues/84) | 196 | [ZapataFrame.md](ZapataFrame.md) | [Zapata](https://drive.google.com/drive/folders/1CvuyOAML9oLtvmFrB-rIOGorJOliTwF_) |
| César Euresti · @cesar-upv | [#85](https://github.com/ZapataFrame/FHCP-Challenge/issues/85) | 195 | [cesar-upv.md](cesar-upv.md) | [Cesar](https://drive.google.com/drive/folders/1sYY6HrJQUxUdfW4p6QDTnwCBs8hAOv1-) |
| Eder Omar Zúñiga Zavala · @KirbyStone69 | [#86](https://github.com/ZapataFrame/FHCP-Challenge/issues/86) | 195 | [KirbyStone69.md](KirbyStone69.md) | [Eder](https://drive.google.com/drive/folders/1GO8g4-chyUJnl6u7ah-2Bjfq6mdfAd3A) |
| Elías de Jesús Zúñiga de León · @ELIASDEJESUSZUNIGADELEON | [#87](https://github.com/ZapataFrame/FHCP-Challenge/issues/87) | 195 | [ELIASDEJESUSZUNIGADELEON.md](ELIASDEJESUSZUNIGADELEON.md) | [Elias](https://drive.google.com/drive/folders/1uNyBfrIoGtrQIRzPa-XLjbJPOGR2j7ut) |

El plan compartido es
[`distributed-fhcp-15x30.json`](../../../experiments/configs/distributed-fhcp-15x30.json),
UUID `8dc498c9-8d26-4e4b-9149-f7abb9b6f285` y digest canónico
`8f79c1b08d83c65c728c7b8b4160e06b74d8cf0dc3c1c200783777d313ee3501`.
Las cinco colas cubren los 1001 candidatos sin solaparse. Cada grafo iniciado
se evalúa con seis algoritmos y 15 semillas (1001–1015), hasta 30 s por intento,
sin límite de evaluaciones/iteraciones. Son 90 intentos por grafo y hasta 45 min
de búsqueda, más sobrecarga.

La meta es **60 grafos distintos con ciclo certificado entre todo el equipo**.
Las colas son reservas; no hay que agotarlas si se alcanza el objetivo. Tras
cada sesión se informa el avance en su issue y se coordina con Arturo la
agregación y parada. Se completan los algoritmos/semillas del grafo iniciado;
los demás candidatos conservan estado pendiente. No hay parada global automática.

## Entrega final

Las cinco carpetas ya existen bajo
[FHCP-results / FHCP-evaluation](https://drive.google.com/drive/folders/1dUm3h-GP8go78XqCSwnCcCZWN9wtvgtb)
en el Drive institucional de Arturo. Se comprobaron sus nombres, padre y
permisos el 14 de noviembre de 2026: Arturo es propietario y los otros cuatro
integrantes tienen edición.

Cada integrante debe subir **a su propia carpeta**:

1. ZIP final completo, generado con `pack`: plan, perfil, snapshot, logs,
   sesiones, RunRecords con rutas, auditorías y tablas.
2. El archivo `.zip.sha256` generado junto al ZIP.
3. `summary.md`, `summary.csv` y `summary.json` como copias consultables.

`pack` solo empaqueta localmente; la subida es manual. Enlazar el ZIP final y
checksum en el issue, junto con grafos completados/resueltos/pendientes,
errores y tiempos observados. Conservar también resultados agotados e
interrumpidos. No reemplazar entregas anteriores ni borrar directorios locales
que puedan necesitar reanudación. Los respaldos iniciales se conservan en
`M6-original-prueba-inicial`.

Arturo verificará integridad y recuperación y combinará las entregas con
`combine` y el plan original para contar grafos distintos certificados.
Se conservan hardware y tiempos por equipo; no se presentan como mediciones
en la misma máquina. Los issues de ejecución permanecen abiertos hasta aceptar
su evidencia; integrar la preparación no acredita haber logrado los 60 grafos
ni cierra M6.

Estos cinco documentos son entregas revisadas para este reparto y añaden Drive,
instalación y seguimiento a los borradores genéricos producidos por `handoff`.
