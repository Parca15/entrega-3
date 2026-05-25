"""Exporta resultados del pipeline a Parquet y CSV."""

from pathlib import Path
from pyspark.sql import DataFrame, functions as F


class ResultExporter:
    """Exporta resultados procesados a disco en formatos columnar y tabular."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir

    def export(self, df: DataFrame) -> None:
        """Escribe los resultados finales en directorios de salida bien estructurados."""
        print("\n[ETAPA 9] Exportando resultados...")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        df_virales = df.filter(F.col("nivel_viral") == "viral")
        output_virales_path = str(self.output_dir / "tweets_virales")
        df_virales.coalesce(1).write.mode("overwrite").parquet(output_virales_path)
        print(f"  → tweets_virales.parquet exportado ({df_virales.count():,} registros)")
        resumen = (
            df.groupBy("pais", "sentimiento").agg(
                F.count("*").alias("total"),
                F.round(F.avg("likes"), 2).alias("avg_likes"),
            ).orderBy("pais", "sentimiento")
        )
        resumen_path = str(self.output_dir / "resumen_pais_sentimiento")
        resumen.coalesce(1).write.mode("overwrite").option("header", "true").csv(resumen_path)
        print("  → resumen_pais_sentimiento.csv exportado")
        particionado_path = str(self.output_dir / "tweets_particionado")
        df.write.mode("overwrite").partitionBy("pais", "anio").parquet(particionado_path)
        print("  → tweets_particionado.parquet exportado (particionado por país/año)")
        print(f"\n[OK] Exportación completada en directorio: {self.output_dir}/")
