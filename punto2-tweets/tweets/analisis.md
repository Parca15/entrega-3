# Análisis del Código Fuente — Proyecto Big Data con PySpark

## Introducción al análisis

Este documento presenta el análisis técnico y crítico del código fuente desarrollado para el procesamiento distribuido de un dataset de 5 millones de tweets sintéticos. El objetivo del análisis no es describir línea por línea lo que hace el código, sino explicar **por qué** se tomaron las decisiones técnicas que se tomaron, cuál es su impacto en el rendimiento del sistema y cómo cada componente justifica el uso de tecnologías Big Data frente a alternativas tradicionales como Pandas.

---

## 0. Arquitectura del código

El proyecto está estructurado en varios archivos de clases independientes:

- `tweets/analisis_tweets.py`: punto de entrada que crea y ejecuta `TweetPipeline`.
- `tweets/spark_manager.py`: clase `SparkManager` para crear y configurar la `SparkSession`.
- `tweets/tweet_dataset.py`: clase `TweetDataset` para carga, limpieza y enriquecimiento del DataFrame.
- `tweets/tweet_analyser.py`: clase `TweetAnalyser` para los análisis exploratorio, de sentimientos, hashtags y ventanas temporales.
- `tweets/result_exporter.py`: clase `ResultExporter` para exportar resultados a Parquet y CSV.
- `tweets/tweet_pipeline.py`: clase `TweetPipeline` que orquesta el pipeline completo.

Separar la funcionalidad en clases y archivos independientes hace el proyecto más mantenible, facilita pruebas y extensiones, y mejora la claridad frente a un único script monolítico.

---

## 1. SparkSession — El punto de partida distribuido

```python
spark = (
    SparkSession.builder
    .appName("BigData_Tweets_Analisis")
    .master("local[*]")
    .config("spark.sql.shuffle.partitions", "8")
    .config("spark.sql.adaptive.enabled", "true")
    .config("spark.driver.memory", "4g")
    .getOrCreate()
)
```

### Análisis crítico

La `SparkSession` es la puerta de entrada al motor distribuido de Spark. La configuración `local[*]` instruye a Spark para que use **todos los núcleos de CPU disponibles** en la máquina local, simulando el paralelismo que en producción se distribuiría entre múltiples nodos de un clúster.

La decisión más relevante aquí es reducir `spark.sql.shuffle.partitions` de su valor por defecto (200) a **8**. Esta decisión tiene un impacto directo en el rendimiento: en operaciones de shuffle (como `groupBy` o `join`), Spark crea 200 particiones por defecto. Con un dataset de 5 millones de filas en una máquina local de 4–8 núcleos, esas 200 particiones generarían overhead de planificación y archivos intermedios innecesariamente pequeños. Reducirlo a 8 alinea el número de particiones con el paralelismo real del entorno.

`spark.sql.adaptive.enabled = true` activa el **Adaptive Query Execution (AQE)**, una característica crítica de Spark 3.x que permite reoptimizar el plan de ejecución en tiempo real. Por ejemplo, si una operación de join detecta que un lado de la tabla es pequeño, AQE lo convierte automáticamente en un *broadcast join* (sin shuffle), lo que puede mejorar el rendimiento en órdenes de magnitud.

**Impacto vs Pandas:** Pandas carga el dataset completo en la RAM de un solo proceso. Con 5 millones de filas y ~15 columnas, esto puede superar los 2–3 GB de memoria. PySpark, en cambio, distribuye el procesamiento en particiones que se ejecutan en paralelo, sin requerir que todo el dataset esté en memoria al mismo tiempo.

---

## 2. Schema explícito — Eficiencia desde la ingesta

```python
StructType([
    StructField("tweet_id",   StringType(),  nullable=False),
    StructField("likes",      IntegerType(), nullable=True),
    StructField("fecha_publicacion", StringType(), nullable=True),
    ...
])
```

### Análisis crítico

Definir el schema de forma explícita en lugar de usar `inferSchema=True` es una decisión de eficiencia con impacto medible. Cuando Spark infiere el schema, realiza un **escaneo completo del CSV** para determinar los tipos de cada columna — sobre 5 millones de registros, esto duplica el tiempo de carga.

Al declarar los tipos explícitamente, se elimina ese escaneo previo y se garantiza que los tipos son exactamente los esperados. La columna `fecha_publicacion` se mantiene como `StringType` deliberadamente en este punto, porque será transformada a `TimestampType` en la etapa de limpieza usando `to_timestamp()` — esta separación mantiene claro el flujo de transformación.

---

## 3. Limpieza de datos — Transformaciones lazy en el DAG

```python
df_limpio = (
    df
    .dropna(subset=["tweet_id", "usuario_id"])
    .withColumn("fecha_ts", F.to_timestamp(F.col("fecha_publicacion"), "yyyy-MM-dd HH:mm:ss"))
    .withColumn("sentimiento", F.trim(F.lower(F.col("sentimiento"))))
    .withColumn("es_retweet",
        F.when(F.lower(F.col("es_retweet")) == "true", True).otherwise(False))
    .filter(F.col("likes") >= 0)
    .dropDuplicates(["tweet_id"])
)
```

### Análisis crítico

Este bloque contiene exclusivamente **transformaciones**, que en Spark son *lazy*: no se ejecutan en el momento en que se declaran. En cambio, Spark registra cada operación en un **DAG (Directed Acyclic Graph)** de transformaciones. Solo cuando se llama a una acción como `count()`, `show()` o `write()`, Spark compila el DAG completo y lo ejecuta de la manera más eficiente posible mediante el **Catalyst Optimizer**.

Esta arquitectura tiene una ventaja fundamental sobre el procesamiento secuencial de Pandas: Spark puede reordenar, combinar o eliminar operaciones innecesarias antes de ejecutarlas. Por ejemplo, si después de un `filter` hay un `groupBy`, Spark puede empujar el filtro hacia abajo en el plan (*predicate pushdown*) para reducir el volumen de datos que participa en el shuffle.

La operación `dropDuplicates(["tweet_id"])` es especialmente relevante en Big Data: requiere un **shuffle global** (todos los datos con el mismo `tweet_id` deben llegar a la misma partición para ser comparados), pero Spark lo maneja distribuyendo el trabajo entre los ejecutores.

---

## 4. Feature Engineering — Paralelismo máximo con transformaciones narrow

```python
df_enriquecido = (
    df
    .withColumn("anio",       F.year("fecha_ts"))
    .withColumn("tasa_engagement",
        F.round(
            (F.col("likes") + F.col("retweets") + F.col("respuestas"))
            / F.greatest(F.col("longitud_texto"), F.lit(1)),
            4
        ))
    .withColumn("nivel_viral",
        F.when(F.col("retweets") >= 10_000, "viral")
         .when(F.col("retweets") >= 1_000,  "trending")
         ...
    )
)
```

### Análisis crítico

Todas las operaciones `withColumn()` aplicadas aquí son **transformaciones narrow**: cada registro de salida depende únicamente del registro de entrada correspondiente, sin necesitar información de otras particiones. Esto significa que Spark puede ejecutarlas en **perfecta independencia** entre particiones, sin ningún intercambio de datos en red.

La métrica `tasa_engagement` es un ejemplo de feature engineering relevante para Big Data: en lugar de calcular métricas en el driver (lo que requeriría `collect()` primero), la fórmula se aplica de forma distribuida sobre cada fila. El uso de `F.greatest(F.col("longitud_texto"), F.lit(1))` evita divisiones por cero de forma vectorizada, sin necesidad de Python puro.

La clasificación `nivel_viral` con `F.when().otherwise()` es el equivalente distribuido de un `if-elif-else`, evaluado sobre millones de filas en paralelo. En Pandas esto sería `np.select()` o `apply()` — pero `apply()` en Pandas ejecuta una función Python fila por fila (GIL), mientras que el `when()` de Spark se compila a código JVM optimizado.

---

## 5. Cache estratégico — Evitar recálculo del DAG

```python
df_enriquecido = enriquecer_datos(df_limpio).cache()
df_enriquecido.count()  # Fuerza la materialización
```

### Análisis crítico

Esta es una de las decisiones de rendimiento más importantes del pipeline. Sin `cache()`, cada acción que se ejecute sobre `df_enriquecido` (los análisis exploratorios, el análisis de sentimientos, la exportación) recalcularía desde cero todas las transformaciones anteriores: lectura del CSV → limpieza → 10+ `withColumn()` → cada acción.

Con `cache()`, Spark materializa el DataFrame en memoria después de la primera acción y lo reutiliza en todas las acciones siguientes. El `count()` que sigue sirve específicamente para **forzar la materialización** del cache antes de que comiencen los análisis, de modo que no se mezcle el tiempo de materialización con el tiempo de análisis.

Este patrón es el análogo distribuido de "calcular una variable una vez y reutilizarla" — fundamental cuando el costo de recálculo es alto (como leer y procesar 5M de registros desde disco).

---

## 6. API de RDD — MapReduce para conteo de hashtags

```python
rdd_textos = df.select("texto").rdd.map(lambda row: row["texto"])

conteo_hashtags = (
    rdd_textos
    .flatMap(lambda texto: [
        (token.lower(), 1)
        for token in (texto or "").split()
        if token.startswith("#") and len(token) > 1
    ])
    .reduceByKey(lambda a, b: a + b)
    .sortBy(lambda par: par[1], ascending=False)
)
```

### Análisis crítico

Esta sección utiliza deliberadamente la **API de RDD de bajo nivel** en lugar del DataFrame API, con el propósito de ilustrar el paradigma **MapReduce** en su forma más explícita.

El flujo implementa el clásico *Word Count* distribuido aplicado a hashtags:

- **`flatMap`**: transforma cada tweet (una entrada) en múltiples pares `(hashtag, 1)` (muchas salidas). Es el equivalente del paso **Map** en MapReduce.
- **`reduceByKey`**: agrupa por clave (hashtag) y suma los valores. Spark aplica primero una **reducción local** en cada partición (como un combiner de Hadoop) antes de hacer el shuffle, minimizando los datos transferidos en red.
- **`sortBy`**: ordena globalmente los pares resultantes por conteo descendente.

**Por qué RDD y no DataFrame aquí:** En el DataFrame API, extraer tokens de una columna de texto requeriría `F.split()` + `F.explode()` + `F.filter()` + `groupBy()`. Con RDD se puede usar cualquier lógica Python pura en el `flatMap`, incluyendo expresiones regulares complejas, sin las restricciones del tipado de columnas. Esto demuestra que ambas APIs tienen su lugar: DataFrame API para la mayoría de las operaciones (por sus optimizaciones), RDD para lógica de transformación compleja o no estándar.

---

## 7. Window Functions — Análisis temporal sin colapso de filas

```python
ventana = Window.orderBy("anio", "mes")

df_con_ventana = (
    df_mensual
    .withColumn("ranking_mensual",    F.rank().over(ventana))
    .withColumn("tweets_mes_anterior", F.lag("total_tweets", 1).over(ventana))
    .withColumn("variacion_pct",
        F.round(
            (F.col("total_tweets") - F.col("tweets_mes_anterior"))
            / F.col("tweets_mes_anterior") * 100, 2
        ))
)
```

### Análisis crítico

Las **Window Functions** representan una de las capacidades más sofisticadas del SQL distribuido. A diferencia de `groupBy`, que colapsa múltiples filas en una sola fila por grupo, las Window Functions calculan valores agregados **manteniendo todas las filas originales**. Esto es esencial para análisis de series temporales.

`F.lag("total_tweets", 1)` calcula el valor del período anterior para cada fila. En SQL tradicional, este tipo de análisis requeriría un self-join de la tabla consigo misma — una operación costosa. Con Window Functions, Spark lo resuelve de forma eficiente con un solo shuffle.

`F.rank().over(ventana)` asigna una posición ordinal a cada mes según el orden temporal. Esto permite identificar directamente cuál mes tuvo más o menos actividad sin necesidad de joins adicionales.

**Impacto en Big Data:** En producción, estas mismas funciones se aplicarían sobre cientos de millones de eventos con particionado por usuario (`PARTITION BY usuario_id ORDER BY fecha`), permitiendo calcular métricas personalizadas para millones de usuarios simultáneamente — algo imposible de escalar con Pandas.

---

## 8. Exportación a Parquet con partition pruning

```python
df.write \
  .mode("overwrite") \
  .partitionBy("pais", "anio") \
  .parquet("resultados/tweets_particionado")
```

### Análisis crítico

La exportación en formato **Parquet** con `partitionBy` es una decisión de arquitectura que impacta todas las consultas futuras sobre estos datos.

**Por qué Parquet:** Es un formato de almacenamiento columnar. Si una consulta futura necesita solo las columnas `likes` y `sentimiento`, Parquet lee únicamente esas dos columnas del disco, ignorando todas las demás. En un CSV, se tendría que leer cada fila completa aunque solo se necesiten 2 de 15 columnas. En un dataset de cientos de GB, esta diferencia puede representar una reducción del 80–90% en I/O de disco.

**Partition pruning:** Al usar `partitionBy("pais", "anio")`, Spark crea una estructura de directorios `pais=CO/anio=2023/`. Si una consulta futura filtra por `pais = 'CO' AND anio = 2023`, Spark accede únicamente al subdirectorio correspondiente, ignorando el resto del dataset. En un escenario real con datos de 10 años y 50 países, esto puede reducir el volumen de datos leídos en un 98%.

---

## Conclusión del análisis

El pipeline desarrollado demuestra los principios fundamentales del procesamiento Big Data con PySpark:

| Principio | Implementación en el proyecto |
|---|---|
| **Evaluación lazy** | Todas las transformaciones se acumulan en el DAG antes de ejecutarse |
| **Paralelismo** | Operaciones narrow ejecutadas sin shuffle en todos los núcleos |
| **Minimizar shuffle** | Cache estratégico, predicate pushdown, reducción de particiones |
| **Formato columnar** | Parquet con particionado para eficiencia en lecturas futuras |
| **Dos niveles de API** | DataFrame API (optimizado) + RDD API (flexible) según el caso |
| **Escalabilidad horizontal** | El mismo código funciona en local y en un clúster de 100 nodos |

La diferencia más significativa frente a Pandas no es solo la capacidad de manejar más datos, sino la **arquitectura de ejecución**: mientras Pandas ejecuta operaciones de forma secuencial en un solo proceso, PySpark construye un plan de ejecución optimizado que puede distribuirse entre cientos de máquinas sin cambiar una sola línea de código de análisis.

---

## Capturas de Pantalla Requeridas

Para documentar la ejecución del pipeline, se deben tomar las siguientes capturas de pantalla durante la ejecución de `analisis_tweets.py`. Cada captura debe mostrar la salida de consola correspondiente a la etapa indicada.

### 1. Inicialización de SparkSession
**Dónde:** Inmediatamente después de ejecutar el script, cuando aparezca la configuración de Spark.  
**Qué capturar:** La salida que muestra "SparkSession iniciada correctamente", versión de Spark, núcleos activos y configuración inicial.  
**Propósito:** Demostrar la configuración correcta del entorno Spark.

### 2. Carga de Dataset
**Dónde:** Después del mensaje "[ETAPA 2] Cargando dataset...".  
**Qué capturar:** Los registros cargados, tiempo de carga y particiones activas.  
**Propósito:** Verificar la ingesta exitosa del CSV y el rendimiento de carga.

### 3. Limpieza de Datos
**Dónde:** Después del mensaje "[ETAPA 3] Limpieza y validación de datos...".  
**Qué capturar:** El número de registros antes y después de la limpieza.  
**Propósito:** Mostrar la efectividad de las transformaciones de limpieza.

### 4. Enriquecimiento de Datos
**Dónde:** Después del mensaje "[ETAPA 4] Enriquecimiento y feature engineering...".  
**Qué capturar:** El mensaje de "Feature engineering completado."  
**Propósito:** Confirmar la adición exitosa de nuevas columnas calculadas.

### 5. Análisis Exploratorio
**Dónde:** Después del mensaje "[ETAPA 5] ANÁLISIS EXPLORATORIO".  
**Qué capturar:** Las tablas de distribución por idioma, top 10 países, estadísticas descriptivas, dispositivos y franjas horarias.  
**Propósito:** Documentar los insights iniciales del dataset.

### 6. Análisis de Sentimientos
**Dónde:** Después del mensaje "[ETAPA 6] ANÁLISIS DE SENTIMIENTOS".  
**Qué capturar:** La distribución global de sentimientos, sentimientos por país y sentimientos vs nivel viral.  
**Propósito:** Mostrar el análisis emocional del contenido de tweets.

### 7. Ranking de Hashtags
**Dónde:** Después del mensaje "[ETAPA 7] RANKING DE HASHTAGS (API RDD)".  
**Qué capturar:** El top 20 de hashtags más usados con sus apariciones.  
**Propósito:** Ilustrar el uso de la API RDD para procesamiento de texto.

### 8. Análisis Temporal
**Dónde:** Después del mensaje "[ETAPA 8] ANÁLISIS TEMPORAL CON WINDOW FUNCTIONS".  
**Qué capturar:** La evolución mensual de tweets con variaciones porcentuales.  
**Propósito:** Demostrar el uso de Window Functions para series temporales.

### 9. Exportación de Resultados
**Dónde:** Después del mensaje "[ETAPA 9] Exportando resultados...".  
**Qué capturar:** La confirmación de archivos exportados (tweets_virales.parquet, resumen_pais_sentimiento.csv, tweets_particionado.parquet).  
**Propósito:** Verificar la correcta exportación en formatos columnar y particionados.

### 10. Métricas de Rendimiento
**Dónde:** Después del mensaje "[ETAPA 10] MÉTRICAS DE RENDIMIENTO DEL PIPELINE".  
**Qué capturar:** El tiempo total de ejecución, memoria del driver, particiones de shuffle y configuración de Spark.  
**Propósito:** Documentar el rendimiento y configuración del pipeline.

### 11. Finalización Exitosa
**Dónde:** Al final de la ejecución.  
**Qué capturar:** El mensaje "[FIN] Pipeline completado exitosamente."  
**Propósito:** Confirmar la terminación correcta de todo el proceso.

**Nota:** Para obtener estas capturas, ejecute el script con `./.venv/bin/python tweets/analisis_tweets.py` y tome las capturas en el orden indicado. Asegúrese de que la ventana de terminal muestre claramente la salida de cada etapa.
