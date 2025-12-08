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


# US-3.1: Agregaçãp Mensal Regional Total (Fato para Picos de Demanda)

# 1. Definir o nível de agregação (Granularidade: Região e Mês)
df_total_regional = df_silver.groupBy(
    "regiao",
    "mes_de_referencia"
).agg(
    F.sum("consumo_em_kwh").alias("consumo_total_kwh"),
    F.sum("valor_da_conta").alias("custo_total"),
    F.count("*").alias("total_registros") # Contagem para entender o volume
)

# 2. Persistência da Tabela Fato
df_total_regional.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.ft_consumo_mensal_regional")

print("Tabela Fato ft_consumo_mensal_regional persistida com sucesso.")

df_total_regional.show(5)

# US-3.2: Agregação por Tipo de Cliente (Fato para Custo/Rentabilidade)

# 1. Definir o nível de agregação (Granularidade: Tipo de Cliente)
df_custo_segmento = df_silver.groupBy(
    "tipo_de_cliente"
).agg(
    F.sum("consumo_em_kwh").alias("consumo_total_kwh"),
    F.sum("valor_da_conta").alias("custo_total"),
    
    # Métrica Chave: Custo médio por kWh para o segmento
    (F.sum("valor_da_conta") / F.sum("consumo_em_kwh")).alias("custo_medio_por_kwh_segmento")
)

# 2. Persistência da Tabela Fato
df_custo_segmento.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.ft_custo_segmento")

print("Tabela Fato ft_custo_segmento persistida com sucesso.")

df_custo_segmento.show()

# US-3.3: Criar a Tabela Dimensional D-Localidade


# 1. Selecionar chaves de negócio únicas
df_localidade_dim = df_silver.select("regiao", "cidade", "bairro").distinct()


# 2. Criar a Chave Substituta (SK)
# Usamos 'monotonically_increasing_id()' para gerar um ID sequencial
df_localidade_dim = df_localidade_dim.withColumn(
    "localidade_sk",
    F.monotonically_increasing_id().cast(LongType())
)


# 3. Persistência da Dimensão D-Localidade
df_localidade_dim.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.d_localidade")


print("Dimensão D-Localidade persistida com sucesso.")


df_localidade_dim.show(5)

# US-5: Agregação Mensal Regional Comparativa (Fato)


# 1. Definir o nível de agregação (Granularidade)
df_consumo_agregado = df_silver.groupBy(
    "regiao",
    "mes_de_referencia",
    "tipo_de_consumo" # Chave principal para o comparativo
).agg(
    F.sum("consumo_em_kwh").alias("consumo_total_kwh"),
    F.sum("valor_da_conta").alias("custo_total"),
    F.sum("valor_de_imposto").alias("imposto_total"),
   
    # Métrica derivada: Custo médio por kWh
    (F.sum("valor_da_conta") / F.sum("consumo_em_kwh")).alias("custo_medio_por_kwh")
)


# 2. Persistência da Tabela Fato
df_consumo_agregado.write.format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(f"{CATALOGO}.{SCHEMA_GOLD}.ft_consumo_mensal_comparativo")


print("Tabela Fato ft_consumo_mensal_comparativo persistida com sucesso.")


df_consumo_agregado.show(5)

# 03 - Agregação da Camada GOLD (Modelagem Dimensional)

## Objetivo
Criar o Modelo de Dados Dimensional (Tabelas FATO e DIMENSÃO) a partir dos dados limpos da Camada Silver, visando otimizar a performance de consultas e responder às User Stories de Negócio.

## User Stories Concluídas
* **US-3.5:** Criação da Dimensão D-Localidade.
* **US-5:** Criação da Fato Comparativa (Geral vs. Limpa).
* **US-3.1:** Criação da Fato Total Regional (Picos de Demanda).
* **US-3.2:** Criação da Fato por Tipo de Cliente (Custo Médio).


## Tabelas Finais Persistidas
1.  **Dimensão:** `d_localidade` (Região, Cidade, Bairro, Localidade_SK)
2.  **Fato 1 (Comparativa):** `ft_consumo_mensal_comparativo` (Agregada por Região, Mês, Tipo de Consumo)
3.  **Fato 2 (Total):** `ft_consumo_total_regional` (Agregada por Região, Mês)
4.  **Fato 3 (Segmento):** `ft_custo_por_segmento` (Agregada por Tipo de Cliente)
