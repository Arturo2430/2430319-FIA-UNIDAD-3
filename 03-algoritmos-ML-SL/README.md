# 03. Algoritmos de aprendizaje automático supervisado

Prácticas de clasificación con ejemplos etiquetados: K-Nearest Neighbors (KNN), árboles de decisión, Random Forest y perceptrones. La carpeta combina notebooks de Python con material de seguimiento del aprendizaje en PDF y hoja de cálculo.

## Trabajo realizado

En KNN se implementó la clasificación por vecinos cercanos utilizando NumPy para las distancias y una votación por mayoría. Se generaron datos sintéticos, se dividieron en entrenamiento y prueba y se compararon regiones de decisión para distintos valores de k.

En árboles y Random Forest se utilizó Iris de scikit-learn, seleccionando longitud y ancho del pétalo como características. Se entrenó un árbol de profundidad máxima dos y un bosque de 67 árboles, y se representaron las reglas del árbol y las regiones de decisión del bosque.

La práctica de perceptrones conserva una tabla de entradas, salidas deseadas, predicciones y pesos por época. El PDF y la hoja de cálculo permiten consultar ese seguimiento; esta carpeta no incluye un script de perceptrón en Python.

## Prácticas

| Carpeta | Material |
| --- | --- |
| [KNN](KNN/) | Notebook de KNN desde cero, evaluación y gráficas. |
| [decision-tree-y-random-forest](decision-tree-y-random-forest/) | Notebook de clasificación de Iris con árbol de decisión y Random Forest. |
| [perceptron](perceptron/) | Registro del aprendizaje del perceptrón en PDF y Excel. |
| [datasets](datasets/) | Copia de Iris en CSV disponible como material de datos. |

## Instalación

Desde la carpeta del proyecto, con Python 3.10 o posterior:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

En Fish, activa el entorno con `source .venv/bin/activate.fish`.

Las dependencias son NumPy, Matplotlib, scikit-learn, Notebook e ipykernel. El material de perceptrones puede consultarse con un visor PDF y una aplicación compatible con XLSX, sin instalar las dependencias de los notebooks.

## Ejecución

Con el entorno activo y desde esta carpeta:

```bash
jupyter notebook
```

Abre `KNN/knn.ipynb` o `decision-tree-y-random-forest/decision-tree.ipynb`, selecciona el kernel del entorno y ejecuta las celdas en orden desde el principio. Los notebooks conservan salidas que permiten consultar ejemplos de ejecución sin volver a calcularlos.

KNN genera sus propios datos y el otro notebook usa `datasets.load_iris()`; ninguno depende del archivo `datasets/Iris.csv`. No es necesario descargar otro dataset para ejecutar estas dos prácticas.
