# Informe del código — Punto 2 (Tweets)

Este informe describe y analiza las principales partes del código dentro de la carpeta `tweets/`. Incluye notas sobre propósito, diseño, puntos clave y lugares sugeridos para capturas de pantalla.

## Resumen de archivos

- [spark_manager.py](punto2-tweets/tweets/spark_manager.py#L1) — Gestión de la SparkSession y validación de Java.
- [tweet_pipeline.py](punto2-tweets/tweets/tweet_pipeline.py#L1) — Orquestador principal del pipeline (carga, análisis, exportación).
- [tweet_dataset.py](punto2-tweets/tweets/tweet_dataset.py#L1) — Carga, limpieza y enriquecimiento del dataset.
- [tweet_analyser.py](punto2-tweets/tweets/tweet_analyser.py#L1) — Análisis exploratorio, sentimientos, hashtags y análisis temporal.
- [result_exporter.py](punto2-tweets/tweets/result_exporter.py#L1) — Exportación a Parquet/CSV y particionado por `pais`/`anio`.
- [generador_datos.py](punto2-tweets/tweets/generador_datos.py#L1) — Generador sintético de `data/tweets_raw.csv`.
- [analisis_tweets.py](punto2-tweets/tweets/analisis_tweets.py#L1) — Script de entrada que ejecuta el pipeline.

---

## 1) `spark_manager.py` — Gestión de Spark

- Propósito: centralizar la creación/configuración de la `SparkSession` usada por todo el proyecto.
- Puntos clave:
  - Busca y ajusta `JAVA_HOME` para JDK 17 (funciones `_locate_java17` y `_validate_java_version`).
  - Configuraciones recomendadas: `spark.sql.shuffle.partitions`, uso de A QE (`spark.sql.adaptive.enabled`) y Arrow para acelerar conversiones.
  - Ajusta `spark.driver.memory` y muestra información al iniciar sesión.
- Impacto: garantiza reproducibilidad en macOS y reduce errores por versión de Java.

Aquí (captura de la clase SparkManager)

---

## 2) `tweet_pipeline.py` — Orquestación

- Propósito: ejecutar paso a paso el pipeline completo: crear sesión, cargar datos, limpiar, enriquecer, analizar y exportar.
- Flujo principal (`run`):
  1. Crear `SparkSession` (vía `SparkManager`).
  2. Verificar existencia del CSV. Si no existe, indica ejecutar `generador_datos.py`.
  3. `TweetDataset.load_data` → `clean_data` → `enrich_data` (cache y count para materializar).
  4. Ejecutar análisis con `TweetAnalyser` (exploratorio, sentimiento, hashtags, temporal).
  5. Exportar resultados con `ResultExporter`.
  6. Mostrar métricas de rendimiento y detener la sesión.

Aquí (captura de `TweetPipeline.run` o de la clase `TweetPipeline`)

---

## 3) `tweet_dataset.py` — Ingestión y preparación

- Componentes:
  - `define_schema()`: schema explícito para evitar inferencia costosa al leer CSV.
  - `load_data()`: lectura con encabezado, encoding UTF-8 y conteo inicial (muestra número de registros y particiones).
  - `clean_data()`: limpieza de nulos, parseo de timestamp, normalización de columnas (`sentimiento`, `idioma`, `pais`), conversión de `es_retweet` a booleano, filtros de calidad y deduplicación.
  - `enrich_data()`: feature engineering — `anio`, `mes`, `dia_semana`, `hora`, `tasa_engagement`, `nivel_viral`, `tiene_hashtag`, `franja_horaria`.
- Observaciones:
  - Buen uso de `schema` y de funciones de Spark (columnas calculadas y `when`).
  - `enrich_data` define niveles de viralidad y tasa de engagement, útiles para análisis posteriores.

Aquí (captura de `TweetDataset.define_schema` y `TweetDataset.enrich_data`)

---

## 4) `tweet_analyser.py` — Análisis

- Métodos principales:
  - `exploratory_analysis(df)`: estadísticas descriptivas (idioma, país, dispositivo, franja horaria, promedios de likes/retweets).
  - `sentiment_analysis(df)`: distribución de sentimientos, relación sentimiento-engagement y pivot por país (top 5 países).
  - `hashtag_ranking(df)`: extracción de hashtags usando la API RDD (flatMap + reduceByKey) y muestra top 20.
  - `time_window_analysis(df)`: análisis mensual con Window Functions (ranking, lag, variación %).
- Observaciones:
  - Mezcla de DataFrame API y RDD API: la extracción de hashtags usa RDD por flexibilidad sobre tokens.
  - Buen uso de `Window` para series temporales.

Aquí (captura de `TweetAnalyser.hashtag_ranking` — extracción RDD y presentación del top)

---

## 5) `result_exporter.py` — Exportaciones

- Exporta:
  - `tweets_virales` en Parquet (coalesce(1) para generar un único archivo por salida viral).
  - `resumen_pais_sentimiento` como CSV con `header=true`.
  - Dataset particionado por `pais` y `anio` en Parquet (`tweets_particionado`).
- Observaciones:
  - Uso de `coalesce(1)` para outputs agregados (útil para entrega, pero no escalable para producción a gran escala).
  - El particionado por país/año facilita consultas posteriores y particionado eficiente.

Aquí (captura de `ResultExporter.export` mostrando rutas y llamadas a `write`)

---

## 6) `generador_datos.py` — Generador sintético

- Propósito: crear `data/tweets_raw.csv` con esquema compatible con el pipeline.
- Parámetros configurables al inicio (NUM_REGISTROS, ARCHIVO_SALIDA, semilla, vocabularios, países, hashtags, sentimientos y pesos).
- Estructura:
  - Funciones helpers (`generar_tweet_texto`, `generar_fecha_aleatoria`, `generar_registro`).
  - Escritura en bloques (BLOQUE = 100_000) para eficiencia de memoria.
- Observaciones:
  - Diseñado para producir grandes volúmenes; para pruebas locales reducir `NUM_REGISTROS`.

Aquí (captura de la sección de parámetros y del `main` que escribe el CSV)

---

## 7) `analisis_tweets.py` — Punto de entrada

- Simple script con:
  - `pipeline = TweetPipeline(csv_path='data/tweets_raw.csv', output_dir='resultados')`
  - `pipeline.run()`
- Indica que la ejecución se inicia desde este archivo (o directamente importando/ejecutando `TweetPipeline`).

Aquí (captura de `analisis_tweets.py` o salida consola tras ejecución)

---

## Recomendaciones y observaciones finales

- Requisitos: `pyspark` y `JDK 17` en el entorno. `spark_manager.py` proporciona advertencias si la versión de Java no coincide.
- Rendimiento: evitar `coalesce(1)` en pipelines productivos; usar particionado y mantener paralelismo.
- Logging: actualmente se imprimen mensajes por `print`; considerar integrar `logging` para niveles y persistencia.
- Pruebas: crear tests unitarios para transformación (`clean_data` / `enrich_data`) usando pequeños DataFrames de ejemplo.

---

## Capturas recomendadas (marcadores)

- Aquí (captura de la clase SparkManager) — [spark_manager.py](punto2-tweets/tweets/spark_manager.py#L1)
- Aquí (captura de `TweetPipeline.run`) — [tweet_pipeline.py](punto2-tweets/tweets/tweet_pipeline.py#L1)
- Aquí (captura de `TweetDataset.define_schema` y `enrich_data`) — [tweet_dataset.py](punto2-tweets/tweets/tweet_dataset.py#L1)
- Aquí (captura de `TweetAnalyser.hashtag_ranking`) — [tweet_analyser.py](punto2-tweets/tweets/tweet_analyser.py#L1)
- Aquí (captura de `ResultExporter.export`) — [result_exporter.py](punto2-tweets/tweets/result_exporter.py#L1)
- Aquí (captura de la configuración y `main` en `generador_datos.py`) — [generador_datos.py](punto2-tweets/tweets/generador_datos.py#L1)
- Aquí (captura de la ejecución final en consola al correr `analisis_tweets.py`) — [analisis_tweets.py](punto2-tweets/tweets/analisis_tweets.py#L1)

---

**Fin del informe.**
