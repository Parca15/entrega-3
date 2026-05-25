"""
=============================================================
 GENERADOR DE DATOS SINTÉTICOS — TWEETS
=============================================================
 Propósito : Crear un dataset de gran volumen que simule
             publicaciones en una red social tipo Twitter.
 Salida     : data/tweets_raw.csv  (~5 millones de registros)
=============================================================
"""

import csv
import random
import uuid
import os
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# PARÁMETROS DEL DATASET
# ─────────────────────────────────────────────
NUM_REGISTROS   = 1000_000          # Volumen que simula Big Data
ARCHIVO_SALIDA  = "data/tweets_raw.csv"
SEMILLA         = 42                 # Para reproducibilidad

random.seed(SEMILLA)

# ─────────────────────────────────────────────
# VOCABULARIO PARA GENERACIÓN ALEATORIA
# ─────────────────────────────────────────────
IDIOMAS    = ["es", "en", "pt", "fr", "de"]
PAISES     = ["CO", "MX", "AR", "US", "BR", "ES", "FR", "DE", "UK", "JP"]
DISPOSITIVOS = ["Android", "iPhone", "Web", "iPad", "TweetDeck"]

HASHTAGS = [
    "#Python", "#BigData", "#AI", "#MachineLearning", "#DataScience",
    "#PySpark", "#Hadoop", "#CloudComputing", "#OpenSource", "#Tech",
    "#DeepLearning", "#NLP", "#DataEngineering", "#Spark", "#ETL",
    "#Kafka", "#Streaming", "#Analytics", "#BI", "#DataViz",
]

PALABRAS_TEXTO = [
    "análisis", "datos", "nube", "red", "modelo", "resultado",
    "experimento", "clúster", "partición", "paralelismo",
    "transformación", "acción", "DataFrame", "RDD", "latencia",
    "throughput", "escalabilidad", "pipeline", "ingesta", "curación",
    "predicción", "entrenamiento", "precisión", "recall", "F1",
    "aprendizaje", "inferencia", "despliegue", "monitoreo", "alerta",
    "visualización", "tablero", "métrica", "KPI", "dashboard",
]

SENTIMIENTOS = ["positivo", "negativo", "neutro"]

# Pesos para simular distribución real de sentimientos
PESOS_SENTIMIENTO = [0.45, 0.30, 0.25]

# ─────────────────────────────────────────────
# FUNCIONES AUXILIARES
# ─────────────────────────────────────────────

def generar_tweet_texto() -> str:
    """Genera un texto de tweet combinando palabras y hashtags."""
    num_palabras = random.randint(5, 25)
    palabras = random.choices(PALABRAS_TEXTO, k=num_palabras)
    num_hashtags = random.randint(0, 3)
    tags = random.sample(HASHTAGS, k=num_hashtags) if num_hashtags > 0 else []
    return " ".join(palabras + tags)


def generar_fecha_aleatoria(inicio: datetime, fin: datetime) -> str:
    """Devuelve un timestamp aleatorio en formato ISO entre inicio y fin."""
    delta = fin - inicio
    segundos_random = random.randint(0, int(delta.total_seconds()))
    return (inicio + timedelta(seconds=segundos_random)).strftime("%Y-%m-%d %H:%M:%S")


def generar_registro(inicio: datetime, fin: datetime) -> list:
    """Genera una fila completa del dataset."""
    tweet_id      = str(uuid.uuid4())
    usuario_id    = f"user_{random.randint(1, 500_000)}"
    texto         = generar_tweet_texto()
    fecha         = generar_fecha_aleatoria(inicio, fin)
    likes         = random.randint(0, 50_000)
    retweets      = random.randint(0, likes)           # retweets ≤ likes
    respuestas    = random.randint(0, retweets // 2 + 1)
    idioma        = random.choice(IDIOMAS)
    pais          = random.choice(PAISES)
    dispositivo   = random.choice(DISPOSITIVOS)
    sentimiento   = random.choices(SENTIMIENTOS, weights=PESOS_SENTIMIENTO, k=1)[0]
    es_retweet    = random.choices([True, False], weights=[0.3, 0.7], k=1)[0]
    num_hashtags  = len([t for t in texto.split() if t.startswith("#")])
    longitud      = len(texto)

    return [
        tweet_id, usuario_id, texto, fecha,
        likes, retweets, respuestas,
        idioma, pais, dispositivo,
        sentimiento, es_retweet,
        num_hashtags, longitud,
    ]


# ─────────────────────────────────────────────
# ENCABEZADO DEL CSV
# ─────────────────────────────────────────────
COLUMNAS = [
    "tweet_id", "usuario_id", "texto", "fecha_publicacion",
    "likes", "retweets", "respuestas",
    "idioma", "pais", "dispositivo",
    "sentimiento", "es_retweet",
    "num_hashtags", "longitud_texto",
]

# ─────────────────────────────────────────────
# GENERACIÓN PRINCIPAL
# ─────────────────────────────────────────────
def main():
    os.makedirs("data", exist_ok=True)

    fecha_inicio = datetime(2022, 1, 1)
    fecha_fin    = datetime(2024, 12, 31)

    print(f"[INFO] Generando {NUM_REGISTROS:,} registros de tweets...")
    print(f"[INFO] Archivo de salida: {ARCHIVO_SALIDA}")

    BLOQUE = 100_000   # Escritura por bloques para eficiencia de memoria

    with open(ARCHIVO_SALIDA, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(COLUMNAS)

        for i in range(0, NUM_REGISTROS, BLOQUE):
            bloque_actual = min(BLOQUE, NUM_REGISTROS - i)
            filas = [generar_registro(fecha_inicio, fecha_fin)
                     for _ in range(bloque_actual)]
            writer.writerows(filas)

            if (i // BLOQUE) % 10 == 0:
                progreso = (i + bloque_actual) / NUM_REGISTROS * 100
                print(f"  → {i + bloque_actual:>10,} registros escritos  ({progreso:.1f}%)")

    print(f"\n[OK] Dataset generado exitosamente en: {ARCHIVO_SALIDA}")
    tam_mb = os.path.getsize(ARCHIVO_SALIDA) / (1024 ** 2)
    print(f"[OK] Tamaño del archivo: {tam_mb:.1f} MB")


if __name__ == "__main__":
    main()
