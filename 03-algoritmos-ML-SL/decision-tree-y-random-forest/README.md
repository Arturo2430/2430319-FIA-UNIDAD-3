# Árbol de decisión y Random Forest

Práctica de clasificación de flores Iris con scikit-learn. El notebook `decision-tree.ipynb` contiene tanto el árbol de decisión como el bosque aleatorio, aunque su nombre mencione únicamente el primero.

## Trabajo realizado

Se cargaron las 150 muestras de Iris con `datasets.load_iris()` y se seleccionaron dos características: longitud y ancho del pétalo. Los datos se dividieron en 70 % de entrenamiento y 30 % de prueba, con estratificación por clase y `random_state=1`.

Se entrenó un `DecisionTreeClassifier` con criterio Gini y profundidad máxima dos. Sus reglas se imprimen como texto para observar las condiciones sobre las medidas del pétalo que llevan a cada clase. Después se entrenó un `RandomForestClassifier` con 67 estimadores, criterio Gini y la misma semilla.

## Representaciones disponibles

El notebook dibuja las regiones de decisión del bosque sobre el plano de las dos características y marca los puntos del conjunto de prueba. La salida textual del árbol permite comparar una secuencia breve de reglas con la clasificación que produce el conjunto de árboles.

También incluye una preparación con `StandardScaler`, ajustada a un subconjunto de entrenamiento de las clases 0 y 1. Los modelos de árbol y bosque se entrenan con las variables originales `X_train`; los datos estandarizados no se utilizan en esos entrenamientos. No se muestra una métrica numérica de exactitud para comparar ambos modelos.

## Ejecución

Instala las dependencias siguiendo el [README de aprendizaje supervisado](../README.md). Desde `03-algoritmos-ML-SL/`, con el entorno activo:

```bash
jupyter notebook decision-tree-y-random-forest/decision-tree.ipynb
```

Ejecuta todas las celdas en orden. Iris se carga desde scikit-learn; el archivo CSV de la carpeta `datasets/` no se utiliza como entrada del notebook.
