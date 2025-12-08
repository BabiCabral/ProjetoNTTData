# Imports e Definição de Schemas
Python
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.window import Window
from pyspark.sql.types import LongType


# Definindo o catálogo e schemas
CATALOGO = "catalogo_energia"
SCHEMA_SILVER = "silver"
SCHEMA_GOLD = "gold"


# Lendo o DataFrame unificado da Camada Silver
df_silver = spark.read.table(f"{CATALOGO}.{SCHEMA_SILVER}.energia_consumo_silver")


print(f"Total de linhas lidas da Silver: {df_silver.count()}")
df_silver.printSchema()