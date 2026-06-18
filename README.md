# 🐑 Proyecto BI: Análisis Descriptivo y Productivo de Lactancia Ovina

Este repositorio contiene el proyecto final del diplomado de Business Intelligence. Presenta una **solución analítica de extremo a extremo** para evaluar y monitorear el rendimiento lechero en ovinos, pasando desde la ingesta de datos crudos hasta un esquema estrella alojado en AWS Aurora y un dashboard interactivo.

## 🎯 1. Problema de Negocio y Dataset

**Pregunta Analítica:**
> *¿Cuál es el comportamiento histórico de la curva de lactancia ovina y cómo impactan los factores biológicos (paridad, etapa de lactancia), operativos (manejo) y ambientales (clima, fase lunar) en el rendimiento lechero diario y acumulado?*

**El Dataset:**
Se utilizan más de 96,000 registros históricos de controles de ordeña provenientes de la Facultad de Medicina Veterinaria y Zootecnia (FMVZ). El volumen y la dimensionalidad del dataset justifican un enfoque de Data Warehousing para permitir cortes dinámicos sin penalizar el rendimiento de las consultas.

## 🏗️ 2. Arquitectura y Modelo Dimensional

Se diseñó un **Esquema de Estrella** puramente descriptivo e implementado en **AWS Aurora PostgreSQL**. El modelo evita explosiones de cardinalidad y separa métricas variables de atributos estáticos.

![Diagrama del Modelo Dimensional](docs/diagrama_modelo.png)

* **Tabla de Hechos:** `fact_milk_control` (Granularidad: Registro individual de ordeña por oveja/día).
* **Dimensiones Core:**
    * `dim_sheep`: Catálogo único de animales.
    * `dim_date`: Implementada como *Role-Playing Dimension* para conectar tanto la fecha del control (`control_date_key`) como la fecha de parto (`lambing_date_key`).
    * `dim_lactation_stage`: Catálogo discretizado de las etapas productivas (Early, Peak, Mid, Late).
* **Dimensiones de Contexto:** `dim_management`, `dim_weather_condition`, `dim_lunar`, `dim_data_quality` (Junk Dimension para banderas lógicas).
* **Data Marts / Vistas:** Se utiliza `vw_sheep_observation_summary` para calcular métricas históricas de las ovejas sin convertir `dim_sheep` en una dimensión de cambio lento (SCD).

## ⚙️ 3. Instrucciones de Ejecución

### Prerrequisitos
* Python 3.10+
* AWS Aurora PostgreSQL en ejecución (Endpoint y credenciales configuradas en un archivo `.env`).

### Paso 1: Inicializar la Base de Datos (DDL)
Conectarse al clúster de Aurora y ejecutar el script de creación de esquema:
```bash
psql -h <TU_ENDPOINT_AWS> -U <TU_USUARIO> -d postgres -f scripts/01_schema_ddl.sql