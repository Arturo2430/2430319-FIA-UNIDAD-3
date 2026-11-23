# 02. Recopilación de un catálogo de anime

Proyecto en Python para recopilar títulos, sinopsis y géneros de anime mediante la API pública de Kitsu. El avance se conserva en SQLite y se exporta a un CSV con las columnas `titulo`, `sinopsis` y `genero`.

## Trabajo realizado

Se implementó una consulta paginada del catálogo que recupera las fichas de anime y sus géneros. El programa identifica cada obra por su ID, evita duplicar registros y guarda las páginas descargadas junto con el cursor de avance, de modo que puede continuar en otra ejecución sin comenzar desde cero.

Para los títulos se prioriza la escritura rōmaji y se buscan alternativas sin caracteres japoneses cuando es necesario. Las sinopsis originales se conservan y se traducen del inglés al español mediante un modelo OPUS-MT ejecutado localmente en CPU con CTranslate2 y SentencePiece. Las traducciones también quedan almacenadas para no repetir el trabajo. Los géneros se convierten a nombres en español, conservando etiquetas propias del anime cuando corresponde.

La exportación genera un catálogo de tres columnas. Los géneros de una misma obra se separan con `|`, los campos ausentes permanecen vacíos y no se deducen géneros a partir de la sinopsis. Las obras sin un título exportable permanecen en la base de datos aunque no aparezcan en el CSV.

## Datos conservados

La carpeta `datos/` contiene `animes.csv` y `catalogo.sqlite3`. El CSV revisado contiene **1,436 registros**, además del encabezado. Ese número describe la copia disponible y puede cambiar al continuar la recopilación. Las temporadas, películas y especiales con IDs diferentes cuentan como registros distintos.

La base permite conservar originales, traducciones y progreso; el CSV es el resultado preparado para consulta y uso posterior. Las traducciones son automáticas y conviene revisar nombres propios y redacción antes de reutilizarlas.

## Instalación

Requiere Python 3.11 o posterior. Desde la carpeta del proyecto:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

En Fish utiliza `source .venv/bin/activate.fish`; en Windows, `.venv\Scripts\activate`.

El entorno se crea en cada equipo. El modelo de traducción se descarga por separado cuando no está disponible en `modelos/opus-en-es/`; ocupa aproximadamente 158 MB. El código fija su revisión y comprueba las sumas SHA-256 de sus archivos. No necesita GPU ni clave de API.

## Ejecución

Para continuar la recopilación desde la base conservada y descargar el modelo si falta:

```bash
python crawler.py --descargar-modelo
```

Una vez preparado el modelo puedes ejecutar `python crawler.py`. La configuración predeterminada realiza hasta 50 solicitudes por sesión, incluyendo reintentos, con cinco segundos entre solicitudes y un máximo de 20 registros por página. Al consumir el presupuesto, guarda el avance y termina; una nueva ejecución continúa desde ese punto.

Para una prueba separada de diez registros, utiliza archivos propios sin alterar el catálogo de la entrega:

```bash
python crawler.py --limite 10 --descargar-modelo \
  --estado datos/prueba.sqlite3 --salida datos/prueba.csv
```

`--limite` establece el máximo total, incluyendo los registros ya guardados en la base seleccionada. No recorta ni elimina lo recopilado anteriormente. El programa consulta los registros accesibles del catálogo, sin garantizar que represente todos los animes existentes ni que la fuente permanezca sin cambios durante la descarga.

### Otros modos

```bash
# Guardar originales sin cargar el traductor ni exportar CSV.
python crawler.py --solo-descargar --max-peticiones 5

# Traducir y exportar lo almacenado, sin consultar Kitsu.
python crawler.py --solo-exportar --descargar-modelo

# Buscar un título con su propia base y salida.
python crawler.py --buscar "Kimetsu no Yaiba" \
  --estado datos/kimetsu.sqlite3 --salida datos/kimetsu.csv --descargar-modelo
```

Cuando el modelo ya está descargado, `--solo-exportar` funciona sin conexión. Para exportar una búsqueda deben repetirse su argumento `--buscar` y la misma ruta `--estado`. Las búsquedas diferentes usan bases separadas.

Las rutas predeterminadas se resuelven respecto de `crawler.py`. Puedes cambiarlas mediante `--estado`, `--salida` y `--modelo`. Consulta todas las opciones con `python crawler.py --help`.

## Pausas y reanudación

El programa respeta las pausas guardadas entre sesiones. Una respuesta 429 detiene las consultas y conserva `Retry-After`, o una espera mínima de 60 segundos si no existe. Una respuesta 403 registra una pausa de al menos una hora. Los errores de red y del servidor tienen reintentos limitados; una respuesta HTML inesperada también interrumpe la consulta.

Al interrumpir con `Ctrl+C`, se conservan los registros confirmados y se intenta exportar lo ya traducido. El CSV se reemplaza de forma atómica para evitar sustituir una salida válida por una exportación incompleta. No deben ejecutarse varias copias sobre la misma base ni reiniciarse para eludir las pausas.

| Código de salida | Significado |
| --- | --- |
| `0` | Ejecución correcta: límite alcanzado o recorrido terminado. |
| `1` | Error. |
| `2` | Pausa por presupuesto, servidor o red. |
| `130` | Interrupción del usuario. |

## Archivos del proyecto

| Archivo o carpeta | Contenido |
| --- | --- |
| `crawler.py` | Consultas, paginación, persistencia, control de sesiones y exportación. |
| `traduccion.py` | Preparación del modelo y traducción local de sinopsis. |
| `requirements.txt` | CTranslate2 y SentencePiece para la traducción. |
| `datos/animes.csv` | Catálogo exportado. |
| `datos/catalogo.sqlite3` | Registros originales, traducciones y progreso. |
| `modelos/` | Modelo descargable utilizado localmente; excluido de Git. |
| `test_crawler.py` | Pruebas de consulta, transformación, exportación y recuperación. |

## Pruebas del proyecto

Desde esta carpeta:

```bash
python -m unittest discover -s . -p 'test_*.py' -v
```

Las pruebas no hacen solicitudes ni requieren descargar el modelo. Cubren paginación, selección de títulos, deduplicación, transacciones, caché de traducciones, CSV, reintentos y pausas.

## Fuentes del proyecto

- [Kitsu](https://kitsu.io/): origen del catálogo y de los géneros.
- [Documentación de su API](https://hummingbird-me.github.io/api-docs/): referencia del servicio consultado.
- [Modelo de traducción utilizado por el código](https://huggingface.co/michaelfeil/ct2fast-opus-mt-en-es/tree/76ec296588e2234f9b7dfad5254219a0f5ecb7af): conversión de OPUS-MT EN→ES para inferencia local.
