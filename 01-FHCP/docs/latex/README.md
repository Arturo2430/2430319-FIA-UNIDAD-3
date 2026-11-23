# Informe técnico FHCP · M7

`report.tex` es el punto de entrada. El PDF final se entrega como `fhcp-report.pdf`.
`fhcp-report-final.pdf` es una copia idéntica para abrir la versión actual con
un nombre distinto de las exportaciones anteriores.
`fhcp-report-22-graphs.pdf` identifica la exportación que incluye las gráficas
acumuladas de los 22 grafos certificados.
El documento está en español, incluye los cinco integrantes y matrículas indicados
por Arturo, el Dr. Said Polanco Martagón y fecha fija de entrega 17 de noviembre de 2026.

## Fuentes y diseño

- Requisitos: `../sources/practice-20261117.pdf`, copia exacta del PDF suministrado.
- Plantilla original: `template/provided-template.tex`, copia sin cambios del texto
  proporcionado por Arturo. Se conserva como referencia; **no es el punto de compilación**.
- La adaptación conserva la paleta verde/dorada, portada geométrica, encabezados,
  jerarquía tipográfica y franja lateral. Usa pdfLaTeX y Latin Modern, opción ya
  prevista en la plantilla, sin requerir la fuente Posterama externa.
- Se reemplazó el contenido del proyecto ajeno por FHCP. No se presenta este diseño
  como plantilla institucional oficial. Se usa `plainnat` para referencias
  autor-año con DOI/URL y se expresa como `s.f.` el portal sin fecha publicada.
- Se reutiliza la investigación/contratos del repositorio y la comparación histórica;
  no se modifica el código de los algoritmos ni se repiten búsquedas.

`provenance.json` identifica requisitos, plantilla y bases experimentales.
Las figuras y tablas proceden de datos aceptados, con hashes en `asset-manifest.json`.
El resumen de M6 (cero éxitos en 900 primarios) se mantiene separado de la evaluación
posterior (345 éxitos en 8,806 intentos y 15 grafos distintos resueltos).

La entrega incluye además las exploraciones cerradas: 118 intentos de la variante
guiada (dos grafos adicionales) y 2,976 intentos de reparación v4 (11 éxitos,
cinco grafos adicionales, cuatro interrupciones). La unión de IDs certificados
contiene 22 grafos, sin mezclar tasas o tiempos entre protocolos. El cierre v4
conserva 48 grafos completos, cuatro parciales, 13 sin iniciar y 924 combinaciones
no ejecutadas; no se retomarán. El corte inmutable y sus certificados están en
`experiments/analysis/closed-explorations-20261117/` desde la raíz del repositorio.

## Regenerar las tablas y figuras

Desde la raíz del repositorio, con CPython y el entorno fijado en el README raíz:

```bash
python -m pip install -r requirements-analysis.txt
python scripts/build_report_assets.py
```

Si el directorio de configuración de Matplotlib no es escribible, puede fijarse
`MPLCONFIGDIR` a una carpeta local escribible, por ejemplo `docs/latex/build/matplotlib`.
Se generan tablas/macros, CSV de estadísticos y figuras PDF, incluidas
las cajas y tablas de las exploraciones cerradas. El manifiesto registra los hashes
de entradas y salidas. No se lanzan solvers ni se cambian datos experimentales.

## Compilar

Se requiere una distribución TeX con `latexmk`, pdfLaTeX, BibTeX y los paquetes
utilizados en `report.tex`: español/Babel, Latin Modern, AMS, graphicx, geometry,
booktabs, tabularx, longtable, fancyhdr, caption, setspace, microtype, xcolor,
colortbl, enumitem, titlesec, TikZ, natbib, xurl, float y hyperref.

Desde `docs/latex`:

```bash
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build report.tex
```

La salida es `build/report.pdf`. `build/` conserva auxiliares y queda ignorado por Git.
Tras comprobarla, se copia a `fhcp-report.pdf` para publicar el PDF entregable.
La compilación no requiere acceder a Drive ni descargar bibliografía. Para compilar
las fuentes fuera del repositorio basta conservar esta carpeta, sus figuras,
tablas y bibliografía; regenerar datos requiere el repositorio completo.

## Verificación de la entrega

Se comprobó la regeneración determinista de activos, sus totales, las matrículas,
la compilación sin citas/referencias indefinidas ni cajas desbordadas y los límites
de texto del PDF. Todas las páginas se renderizaron y revisaron; se inspeccionaron
además portada, tablas, figuras y parámetros a mayor resolución.

```bash
pdfinfo build/report.pdf
pdftoppm -r 100 -png build/report.pdf build/page
```

`verification.json` registra entorno, entradas, hashes, páginas y resultados.
Las pruebas del código no sustituyen esta revisión visual. La recompilación puede
cambiar metadatos temporales del PDF; las cifras y los activos deben conservarse.

La base actual es `experiments/results/team-evaluation-consolidated-20261117/`.
Se conservan 7,563 intentos seriales y 1,243 paralelos; las medias conjuntas
son descriptivas y no miden aceleración. `execution-modes.csv` identifica cada intento.

Los diagramas de cajas muestran tiempos (todos los intentos y solo éxitos) y
costo final normalizado, por familia y modo serial/paralelo, en grafos completos.
Incluyen tamaño muestral, mediana, cuartiles, bigotes de 1.5 IQR y puntos exteriores.

`scripts/build_exploratory_report_assets.py`, invocado por el generador principal,
usa exclusivamente el corte cerrado. Sus tasas y cajas usan los 48 grafos con
60 combinaciones v4, equivalentes a 480 intentos por familia. La tabla total
conserva además las interrupciones y los cuatro parciales. La sección adicional
y el anexo muestran también costos previos/finales y cobertura de los 65 grafos.

El balance acumulado aparece al inicio de resultados: 22 grafos certificados
entre 149 grafos con intentos. La matriz incluye los 22 IDs con su protocolo y
denominador; la cobertura por familia elimina duplicados y la dispersión de costos
incorpora el mínimo observado en todas las entregas. Las comparaciones de tasas
y las cajas conservan sus grupos por protocolo para mantener sus condiciones.
