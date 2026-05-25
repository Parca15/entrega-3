"""Operaciones de carga, limpieza y enriquecimiento del dataset de tweets."""

import time
from pyspark.sql import DataFrame, SparkSession, functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
)


class TweetDataset:
    """Encapsula la lógica de ingestión y preparación del DataFrame de tweets."""

    @staticmethod
    def define_schema() -> StructType:
        """Define explícitamente el schema del CSV para evitar inferencia costosa."""
        return StructType([
            StructField("tweet_id", StringType(), nullable=False),
            StructField("usuario_id", StringType(), nullable=False),
            StructField("texto", StringType(), nullable=True),
            StructField("fecha_publicacion", StringType(), nullable=True),
            StructField("likes", IntegerType(), nullable=True),
            StructField("retweets", IntegerType(), nullable=True),
            StructField("respuestas", IntegerType(), nullable=True),
            StructField("idioma", StringType(), nullable=True),
            StructField("pais", StringType(), nullable=True),
            StructField("dispositivo", StringType(), nullable=True),
            StructField("sentimiento", StringType(), nullable=True),
            StructField("es_retweet", StringType(), nullable=True),
            StructField("num_hashtags", IntegerType(), nullable=True),
            StructField("longitud_texto", IntegerType(), nullable=True),
        ])

    @staticmethod
    def load_data(spark: SparkSession, path: str) -> DataFrame:
        """Carga el CSV en un DataFrame usando el schema definido."""
        print("\n[ETAPA 2] Cargando dataset...")
        t0 = time.time()
        df = (
            spark.read
            .option("header", "true")
            .option("encoding", "UTF-8")
            .option("multiLine", "false")
            .schema(TweetDataset.define_schema())
            .csv(path)
        )
        total = df.count()
        print(f"  → Registros cargados : {total:>12,}")
        print(f"  → Tiempo de carga    : {time.time() - t0:.2f}s")
        print(f"  → Particiones activas: {df.rdd.getNumPartitions()}")
        return df

    @staticmethod
    def clean_data(df: DataFrame) -> DataFrame:
        """Aplica limpieza de calidad de datos y normalizaciones básicas."""
        print("\n[ETAPA 3] Limpieza y validación de datos...")
        df_limpio = (
            df
            .dropna(subset=["tweet_id", "usuario_id"])
            .withColumn("fecha_ts", F.to_timestamp(F.col("fecha_publicacion"), "yyyy-MM-dd HH:mm:ss"))
            .drop("fecha_publicacion")
            .withColumn("sentimiento", F.trim(F.lower(F.col("sentimiento"))))
            .withColumn("idioma", F.trim(F.lower(F.col("idioma"))))
            .withColumn("pais", F.trim(F.upper(F.col("pais"))))
            .withColumn("dispositivo", F.trim(F.col("dispositivo")))
            .withColumn(
                "es_retweet",
                F.when(F.lower(F.col("es_retweet")) == "true", True).otherwise(False),
            )
            .filter(F.col("likes") >= 0)
            .filter(F.col("retweets") >= 0)
            .filter(F.col("longitud_texto") > 0)
            .dropDuplicates(["tweet_id"])
        )
        total_limpio = df_limpio.count()
        print(f"  → Registros tras limpieza: {total_limpio:>12,}")
        return df_limpio

    @staticmethod
    def enrich_data(df: DataFrame) -> DataFrame:
        """Genera nuevas columnas relevantes para análisis de Big Data."""
        print("\n[ETAPA 4] Enriquecimiento y feature engineering...")
        df_enriquecido = (
            df
            .withColumn("anio", F.year("fecha_ts"))
            .withColumn("mes", F.month("fecha_ts"))
            .withColumn("dia_semana", F.dayofweek("fecha_ts"))
            .withColumn("hora", F.hour("fecha_ts"))
            .withColumn(
                "tasa_engagement",
                F.round(
                    (F.col("likes") + F.col("retweets") + F.col("respuestas"))
                    / F.greatest(F.col("longitud_texto"), F.lit(1)),
                    4,
                ),
            )
            .withColumn(
                "nivel_viral",
                F.when(F.col("retweets") >= 10_000, "viral")
                .when(F.col("retweets") >= 1_000, "trending")
                .when(F.col("retweets") >= 100, "popular")
                .otherwise("normal"),
            )
            .withColumn("tiene_hashtag", F.col("num_hashtags") > 0)
            .withColumn(
                "franja_horaria",
                F.when((F.col("hora") >= 6) & (F.col("hora") < 12), "mañana")
                .when((F.col("hora") >= 12) & (F.col("hora") < 18), "tarde")
                .when((F.col("hora") >= 18) & (F.col("hora") < 24), "noche")
                .otherwise("madrugada"),
            )
        )
        print("  → Feature engineering completado.")
        return df_enriquecido
