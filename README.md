# ProjetoNTTData - Energia Elétrica
# ⚡️ Pipeline de Energia: Ingestão, Tratamento e Análise (Databricks/PySpark)

## 🎯 Objetivo do Projeto

Este projeto implementa um pipeline de ETL (Extract, Transform, Load) completo para ingestão, limpeza, transformação e modelagem de dados de consumo e custo de energia. O objetivo é fornecer conjuntos de dados analíticos prontos (Data Warehouse/Camada Gold) para relatórios de Business Intelligence (BI) e *data science*.

O pipeline foi construído seguindo a arquitetura **Medalhão (Bronze, Silver, Gold)**, utilizando o **Databricks** como plataforma unificada e **PySpark/SQL** como linguagem de processamento.

---

## 🏗️ Arquitetura e Tecnologia

| Componente | Tecnologia Principal | Função |
| :--- | :--- | :--- |
| **Plataforma** | **Databricks** | Ambiente unificado para desenvolvimento e execução de jobs Spark. |
| **Armazenamento** | **Delta Lake** | Formato de tabela aberta para garantir atomicidade, consistência, isolamento e durabilidade (ACID) e versionamento dos dados. |
| **Processamento** | **PySpark** e **SQL** | Linguagem principal para manipulação de DataFrames e transformações de dados. |
| **Modelagem** | **Dimensional** | Implementação de tabelas Fato e Dimensão na Camada Gold. |

---

## 🌊 Fluxo de Dados (Arquitetura Medalhão)

| Camada | Propósito | Principais Ações |
| :--- | :--- | :--- |
| **Bronze** | Ingestão bruta (Landing Zone) | Ingestão inicial de CSVs. Criação de metadados de origem (`nome_arquivo_origem`). |
| **Silver** | Limpeza e Padronização | **US-1: Separação** (Dados Nacionais vs. EUA/2025). **Limpeza** (tratamento de nulos, conversão de tipos, tradução de códigos de cliente, padronização de regiões e meses). **Unificação** dos DataFrames Geral e Limpa. |
| **Gold** | Modelagem Analítica (DW) | Criação de Dimensões e Fatos agregados, otimizados para consultas de BI. |

---

## 📊 Modelagem Analítica (Camada Gold)

A Camada Gold contém as seguintes tabelas Fato e Dimensão, que atendem diretamente aos requisitos de negócio (User Stories):

### Tabelas Fato (ft\_)

| Tabela | Granularidade | User Story Atendida |
| :--- | :--- | :--- |
| `ft_consumo_mensal_regional` | Consumo e Custo por Região e Mês | **US-3.1:** Análise de Tendências e Picos de Demanda. |
| `ft_custo_segmento` | Custo Médio por Kw/h por Tipo de Cliente | **US-3.2:** Avaliação de Precificação e Rentabilidade. |
| `ft_consumo_mensal_cidade` | Consumo e Custo agregado por Cidade e Mês | **US-3.4:** Comparativo de Uso Energético entre Cidades. |
| `ft_consumo_mensal_comparativo` | Consumo por Mês e Tipo de Consumo (Geral vs. Limpa) | **US-5:** Comparativo de fontes de energia. |

### Tabelas Dimensão (d\_)

| Tabela | Granularidade | Função |
| :--- | :--- | :--- |
| `d_localidade` | Região, Cidade e Bairro | **US-3.3:** Permite filtragem geográfica granular em painéis de BI. |

---

## 🛠️ Como Executar o Projeto

1.  **Configuração do Ambiente:** Necessário um cluster Databricks (versão DBR 11.3 LTS ou superior recomendada) com suporte ao Delta Lake.
2.  **Ingestão de Dados:** Certifique-se de que os arquivos CSV brutos (`*2023.csv`, `*2024.csv`, `*2025.csv`) estejam acessíveis no caminho definido para a Camada Bronze (volume/path).
3.  **Execução Sequencial:** Os notebooks devem ser executados na ordem da arquitetura:
    * `notebook_bronze.py` (ou notebook de Ingestão)
    * `notebook_silver.py` (Limpeza e Separação)
    * `notebook_gold.py` (Modelagem Analítica)
