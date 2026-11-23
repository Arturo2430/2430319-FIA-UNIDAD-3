# K-Nearest Neighbors (KNN) desde cero

Práctica de clasificación mediante vecinos cercanos. El notebook `knn.ipynb` implementa el modelo con NumPy y `Counter`, sin utilizar el clasificador KNN de scikit-learn. Scikit-learn se utiliza para generar el conjunto sintético con `make_blobs`.

## Trabajo realizado

Se generaron 300 muestras con dos características y tres clases, usando una semilla fija. Se representaron los puntos y los centros de los grupos, y después se implementó una división aleatoria de 225 muestras de entrenamiento y 75 de prueba.

La clase `KNN` almacena los ejemplos etiquetados en `fit`. Para clasificar un punto calcula las distancias euclidianas a los ejemplos de entrenamiento, selecciona los k más cercanos y elige la etiqueta más frecuente. El método `score` calcula la proporción de aciertos sobre las etiquetas de prueba.

## Resultados disponibles

La salida guardada para k = 5 registra **100 % de exactitud sobre las 75 muestras de prueba** de este conjunto sintético. También se muestran las primeras predicciones junto con las etiquetas reales y una gráfica de las fronteras de decisión.

El notebook compara adicionalmente k = 1, 3, 7 y 15 para observar cómo cambia la clasificación del plano. El resultado corresponde a los datos y a la partición del ejercicio; no representa una precisión garantizada en otros problemas.

## Ejecución

Instala las dependencias siguiendo el [README de aprendizaje supervisado](../README.md). Desde `03-algoritmos-ML-SL/`, con el entorno activo:

```bash
jupyter notebook KNN/knn.ipynb
```

Ejecuta las celdas en orden para generar los datos, dividirlos, definir el modelo y reproducir las gráficas.
