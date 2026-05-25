"""Gestión de SparkSession para el pipeline de análisis de tweets."""

import os
import re
import subprocess
from pathlib import Path

try:
    from pyspark.sql import SparkSession
except ModuleNotFoundError as exc:
    raise ModuleNotFoundError(
        "PySpark no está instalado en este entorno. "
        "Ejecuta: python -m pip install pyspark"
    ) from exc


class SparkManager:
    """Configura y crea la SparkSession usada por todo el proyecto."""

    APP_NAME = "BigData_Tweets_Analisis"
    SHUFFLE_PARTITIONS = "8"
    DRIVER_MEMORY = "4g"

    @staticmethod
    def _locate_java17() -> str | None:
        """Intentar encontrar un JDK 17 instalado en macOS."""
        java_home = os.environ.get("JAVA_HOME")
        if java_home:
            return java_home

        if os.name == "posix" and Path("/usr/libexec/java_home").exists():
            try:
                return subprocess.check_output(
                    ["/usr/libexec/java_home", "-v", "17"],
                    text=True,
                ).strip()
            except subprocess.CalledProcessError:
                return None
        return None

    @staticmethod
    def _validate_java_version() -> None:
        """Valida el JDK usado por Spark y muestra advertencias claras si no es compatible."""
        java_home = SparkManager._locate_java17()
        if java_home:
            os.environ["JAVA_HOME"] = java_home

        java_exec = os.path.join(java_home, "bin", "java") if java_home else "java"
        try:
            result = subprocess.run(
                [java_exec, "-version"],
                capture_output=True,
                text=True,
                check=True,
            )
            version_output = result.stderr.strip() or result.stdout.strip()
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[ADVERTENCIA] No se pudo determinar la versión de Java. Asegúrate de tener JDK 17 instalado.")
            return

        match = re.search(r'version "(\d+)(?:\.(\d+))?', version_output)
        if not match:
            print("[ADVERTENCIA] No se pudo analizar la versión de Java del sistema.")
            return

        major = int(match.group(1))
        if major == 1 and match.group(2):
            major = int(match.group(2))

        if major != 17:
            print("[ADVERTENCIA] Spark 4.x funciona mejor con Java 17.")
            print(f"  Java detectado: {version_output.splitlines()[0]}")
            if java_home:
                print(f"  Ajustando JAVA_HOME a: {java_home}")
            else:
                print("  Si el problema persiste, establece JAVA_HOME con un JDK 17 e inténtalo de nuevo.")

    @staticmethod
    def create_session() -> SparkSession:
        """Crea la SparkSession con configuraciones optimizadas para ejecución local."""
        SparkManager._validate_java_version()

        spark = (
            SparkSession.builder
            .appName(SparkManager.APP_NAME)
            .master("local[*]")
            .config("spark.sql.shuffle.partitions", SparkManager.SHUFFLE_PARTITIONS)
            .config("spark.sql.adaptive.enabled", "true")
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true")
            .config("spark.driver.memory", SparkManager.DRIVER_MEMORY)
            .config("spark.sql.execution.arrow.pyspark.enabled", "true")
            .config("spark.sql.warehouse.dir", str(Path.cwd() / "spark-warehouse"))
            .getOrCreate()
        )
        spark.sparkContext.setLogLevel("ERROR")
        print("=" * 60)
        print(" SparkSession iniciada correctamente")
        print(f" Versión de Spark : {spark.version}")
        print(f" Núcleos activos  : {spark.sparkContext.defaultParallelism}")
        print("=" * 60)
        return spark
