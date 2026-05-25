"""Pipeline principal que coordina Spark, carga, análisis y exportación."""

import time
from pathlib import Path
from spark_manager import SparkManager
from tweet_dataset import TweetDataset
from tweet_analyser import TweetAnalyser
from result_exporter import ResultExporter


class TweetPipeline:
    """Orquesta todas las etapas del pipeline de análisis de tweets."""

    def __init__(self, csv_path: str, output_dir: str):
        self.csv_path = Path(csv_path)
        self.output_dir = Path(output_dir)
        self.spark = None

    def run(self) -> None:
        """Ejecuta el pipeline completo paso a paso."""
        t_inicio = self._start_timer()
        self.spark = SparkManager.create_session()
        if not self.csv_path.exists():
            print(f"\n[ERROR] No se encontró el dataset en: {self.csv_path}")
            print("  Ejecute primero: python generador_datos.py")
            self.spark.stop()
            return
        df_crudo = TweetDataset.load_data(self.spark, str(self.csv_path))
        df_limpio = TweetDataset.clean_data(df_crudo)
        df_enriquecido = TweetDataset.enrich_data(df_limpio).cache()
        df_enriquecido.count()
        TweetAnalyser.exploratory_analysis(df_enriquecido)
        TweetAnalyser.sentiment_analysis(df_enriquecido)
        TweetAnalyser.hashtag_ranking(df_enriquecido)
        TweetAnalyser.time_window_analysis(df_enriquecido)
        ResultExporter(self.output_dir).export(df_enriquecido)
        self._show_metrics(t_inicio)
        df_enriquecido.unpersist()
        self.spark.stop()
        print("\n[FIN] Pipeline completado exitosamente.")

    @staticmethod
    def _start_timer() -> float:
        return time.time()

    def _show_metrics(self, t_inicio: float) -> None:
        t_total = time.time() - t_inicio
        print("\n" + "=" * 60)
        print(" [ETAPA 10] MÉTRICAS DE RENDIMIENTO DEL PIPELINE")
        print("=" * 60)
        print(f"  Tiempo total de ejecución : {t_total:.2f} segundos")
        print(f"  Memoria driver configurada: {SparkManager.DRIVER_MEMORY}")
        print(f"  Particiones de shuffle    : {self.spark.conf.get('spark.sql.shuffle.partitions')}")
        print(f"  Adaptive Query Execution  : {self.spark.conf.get('spark.sql.adaptive.enabled')}")
        print(f"  Arrow habilitado          : {self.spark.conf.get('spark.sql.execution.arrow.pyspark.enabled')}")
        print("=" * 60)
