"""Funciones de análisis exploratorio, de sentimientos y de hashtags."""

from pyspark.sql import DataFrame, functions as F
from pyspark.sql.window import Window


class TweetAnalyser:
    """Contiene los métodos de análisis estadístico y de series temporales."""

    @staticmethod
    def exploratory_analysis(df: DataFrame) -> None:
        """Imprime estadísticas y distribuciones relevantes del dataset."""
        print("\n" + "=" * 60)
        print(" [ETAPA 5] ANÁLISIS EXPLORATORIO")
        print("=" * 60)
        print("\n► Distribución de tweets por idioma:")
        df.groupBy("idioma").agg(
            F.count("*").alias("total_tweets"),
            F.round(F.avg("likes"), 2).alias("promedio_likes"),
            F.round(F.avg("retweets"), 2).alias("promedio_retweets"),
        ).orderBy(F.desc("total_tweets")).show(10, truncate=False)
        print("► Top 10 países por volumen de tweets:")
        df.groupBy("pais").agg(
            F.count("*").alias("total_tweets"),
            F.sum("likes").alias("total_likes"),
        ).orderBy(F.desc("total_tweets")).show(10, truncate=False)
        print("► Estadísticas descriptivas (likes, retweets, longitud):")
        df.select("likes", "retweets", "respuestas", "longitud_texto", "tasa_engagement").describe().show(truncate=False)
        print("► Tweets por dispositivo:")
        df.groupBy("dispositivo").count().withColumnRenamed("count", "total").orderBy(F.desc("total")).show(truncate=False)
        print("► Actividad por franja horaria:")
        df.groupBy("franja_horaria").agg(
            F.count("*").alias("tweets"),
            F.round(F.avg("likes"), 2).alias("avg_likes"),
        ).orderBy(F.desc("tweets")).show(truncate=False)

    @staticmethod
    def sentiment_analysis(df: DataFrame) -> None:
        """Analiza la distribución de sentimientos y su relación con engagement."""
        print("\n" + "=" * 60)
        print(" [ETAPA 6] ANÁLISIS DE SENTIMIENTOS")
        print("=" * 60)
        total = df.count()
        print("\n► Distribución global de sentimientos:")
        df.groupBy("sentimiento").agg(
            F.count("*").alias("cantidad"),
            F.round(F.avg("likes"), 2).alias("avg_likes"),
            F.round(F.avg("retweets"), 2).alias("avg_retweets"),
            F.round(F.avg("tasa_engagement"), 4).alias("avg_engagement"),
        ).withColumn("porcentaje", F.round(F.col("cantidad") / total * 100, 2)).orderBy(F.desc("cantidad")).show(truncate=False)
        print("► Sentimiento por país (top 5 países):")
        top_paises = [row["pais"] for row in df.groupBy("pais").count().orderBy(F.desc("count")).limit(5).collect()]
        df.filter(F.col("pais").isin(top_paises)).groupBy("pais").pivot("sentimiento", ["positivo", "negativo", "neutro"]).count().orderBy("pais").show(truncate=False)
        print("► Sentimiento vs nivel viral:")
        df.groupBy("sentimiento", "nivel_viral").count().orderBy("sentimiento", F.desc("count")).show(20, truncate=False)

    @staticmethod
    def hashtag_ranking(df: DataFrame) -> None:
        """Extrae y ordena los hashtags más frecuentes usando la API RDD."""
        print("\n" + "=" * 60)
        print(" [ETAPA 7] RANKING DE HASHTAGS (API RDD)")
        print("=" * 60)
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
        top_20 = conteo_hashtags.take(20)
        print("\n► Top 20 hashtags más usados:")
        print(f"  {'Posición':<10} {'Hashtag':<25} {'Apariciones':>12}")
        print("  " + "-" * 50)
        for idx, (tag, conteo) in enumerate(top_20, start=1):
            print(f"  {idx:<10} {tag:<25} {conteo:>12,}")

    @staticmethod
    def time_window_analysis(df: DataFrame) -> None:
        """Aplica Window Functions para analizar la evolución mensual de tweets."""
        print("\n" + "=" * 60)
        print(" [ETAPA 8] ANÁLISIS TEMPORAL CON WINDOW FUNCTIONS")
        print("=" * 60)
        df_mensual = (
            df.groupBy("anio", "mes").agg(
                F.count("*").alias("total_tweets"),
                F.sum("likes").alias("total_likes"),
                F.round(F.avg("tasa_engagement"), 4).alias("avg_engagement"),
            ).withColumn("periodo", F.concat(F.col("anio"), F.lit("-"), F.lpad(F.col("mes"), 2, "0")))
        )
        ventana = Window.orderBy("anio", "mes")
        df_con_ventana = (
            df_mensual
            .withColumn("ranking_mensual", F.rank().over(ventana))
            .withColumn("tweets_mes_anterior", F.lag("total_tweets", 1).over(ventana))
            .withColumn(
                "variacion_pct",
                F.round((F.col("total_tweets") - F.col("tweets_mes_anterior")) / F.col("tweets_mes_anterior") * 100, 2),
            )
            .orderBy("anio", "mes")
        )
        print("\n► Evolución mensual de tweets con variación %:")
        df_con_ventana.select("periodo", "total_tweets", "tweets_mes_anterior", "variacion_pct", "avg_engagement").show(36, truncate=False)
