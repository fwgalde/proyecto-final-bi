# Data Warehouse para el análisis de producción lechera ovina

**Autor:** Fernando
**Contexto:** Proyecto final implementado para el Diplomado *Manejo de bases de datos SQL y NoSQL en un entorno de nube* (UNAM).

Solución de Business Intelligence para analizar la producción de leche ovina según días en lactancia, contexto de manejo, condiciones climáticas y calendario temporal. 

El proyecto implementa un modelo dimensional en Amazon Aurora PostgreSQL, un pipeline ETL transaccional y reproducible en Python, consultas SQL analíticas avanzadas y un dashboard interactivo en Power BI soportado por una capa semántica.

## Estado del proyecto

- [x] Definición del problema
- [x] Auditoría de las fuentes
- [x] Diseño dimensional
- [x] DDL en Amazon Aurora PostgreSQL
- [x] ETL Python (Transaccional e idempotente)
- [x] Implementación en AWS
- [x] SQL avanzado (Funciones de ventana, CTEs, PL/pgSQL)
- [x] Capa semántica para Power BI (Role-Playing Views)
- [x] Dashboard interactivo
- [x] Hallazgos y documentación final

## Pregunta analítica

> *¿Cómo varía la producción total de leche registrada por control según los días en lactancia, las condiciones climáticas del día y del día anterior, el corral y el espacio de grupo?*

**Nota:** El análisis es descriptivo y exploratorio. Las asociaciones observadas no implican causalidad.

## Dataset

La fuente principal es el libro de Excel: `datasets/raw/raw_data.xlsx`

**Hojas utilizadas:**
* `Hoja1`: Observaciones de producción y contexto ambiental/manejo.
* `CODIGOS ANIMALES`: Lookup de códigos anonimizados para cada espécimen.

**Características del conjunto:**
| Indicador | Resultado |
| :--- | :--- |
| **Observaciones** | 96,195 |
| **Columnas fuente** | 57 |
| **Ovejas** | 13,829 |
| **Inicio de controles** | 2016-03-10 |
| **Fin de controles** | 2016-06-29 |
| **Producción promedio** | 2.2231 L |
| **Producción mediana** | 2.1100 L |
| **Producción mínima** | 0.1000 L |
| **Producción máxima** | 6.6900 L |
| **Litros totales registrados**| 213,848.17 L |

## Arquitectura

```text
raw_data.xlsx
      │
      ▼
Python ETL (pandas, SQLAlchemy)
      │
      ▼
Amazon Aurora PostgreSQL
├── sheep_dw (Capa Atómica)
│   ├── dim_sheep
│   ├── dim_date
│   ├── dim_lactation_stage
│   ├── dim_management
│   ├── dim_weather_condition
│   ├── dim_lunar
│   ├── dim_data_quality
│   └── fact_milk_control
│
└── sheep_mart (Capa Semántica)
    ├── pbi_dim_*
    └── pbi_fact_milk_control
      │
      ▼
Power BI (Import Mode)

```

## Modelo dimensional

El modelo utiliza un esquema estrella diseñado para evitar la explosión de cardinalidad y asegurar un alto rendimiento en consultas analíticas.

* **Grano:** Una fila de `fact_milk_control` representa una observación individual registrada en una fila física de `Hoja1` del Excel origen.
* **Tabla de hechos (`sheep_dw.fact_milk_control`):** Contiene la producción matutina, vespertina y total, los días en lactancia, el clima exacto del día de control y del día anterior, y las llaves subrogadas hacia todas las dimensiones.

**Dimensiones Core y de Contexto:**

| Dimensión | Descripción |
| --- | --- |
| `dim_sheep` | Identidad anonimizada de cada oveja. |
| `dim_date` | Calendario continuo reutilizado (Role-Playing) para fechas de control y parto. |
| `dim_lactation_stage` | Rangos operativos estáticos de días en lactancia (Buckets). |
| `dim_management` | Combinación única de espacio de grupo y corral. |
| `dim_weather_condition` | Categorías climáticas (viento y precipitación). |
| `dim_lunar` | Contexto de fases lunares. |
| `dim_data_quality` | Junk dimension para el estado de completitud del registro. |

*La dimensión fecha, clima y luna se reutilizan como **dimensiones de rol**. Para Power BI, se exponen vistas independientes en el esquema `sheep_mart` para cada rol, permitiendo relaciones activas y unidireccionales de forma nativa.*

## Estructura del repositorio

```text
proyecto_final_bi/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
│
├── datasets/
│   └── raw/
│       └── raw_data.xlsx
│
├── scripts/
│   ├── 01_schema_ddl.sql           # Esquema estrella y catálogos estáticos
│   ├── 02_advanced_queries.sql     # Consultas analíticas, CTEs y Window Functions
│   ├── 03_views_dashboard.sql      # Capa semántica para Power BI
│   ├── 04_findings.sql             # SQL para extracción de hallazgos
│   └── etl_pipeline.py             # Pipeline de extracción, limpieza y carga
│
├── dashboard/
│   └── powerbi/
│       ├── sheep_milk_analysis.pbix
│       ├── sheep_milk_analysis.pdf
│       └── measures.dax
│
└── docs/
    ├── diagrama_modelo.png
    ├── diagrama_modelo.md
    ├── model_design.md
    ├── data_dictionary.md
    ├── findings.md
    ├── aws_setup.md
    ├── screenshots/
    └── sql_outputs/

```

## Instalación y Configuración

**1. Crear y activar el entorno virtual:**

```bash
python -m venv .venv
# En Windows:
.venv\Scripts\Activate.ps1
# En Linux/macOS:
source .venv/bin/activate

```

**2. Instalar dependencias:**

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt

```

**3. Configurar variables de entorno:**
Crea un archivo `.env` en la raíz (no rastreado por Git) usando la plantilla:

```bash
cp .env.example .env

```

Asegúrate de llenar las credenciales de tu clúster de AWS Aurora:

```env
SOURCE_FILE=datasets/raw/raw_data.xlsx
DB_HOST=<AURORA_ENDPOINT>
DB_PORT=5432
DB_NAME=<DATABASE_NAME>
DB_USER=<DATABASE_USER>
DB_PASSWORD=<DATABASE_PASSWORD>
DB_SSLMODE=require
DB_CONNECT_TIMEOUT=20
ETL_CHUNK_SIZE=500

```

## Despliegue en AWS Aurora

**1. Crear el modelo físico (DDL):**

Hecho a través de DBeaver. 

*Este script realiza una construcción limpia: crea los esquemas `sheep_dw` y `sheep_mart`, las restricciones analíticas (`CHECK`), índices sobre llaves foráneas y puebla los catálogos estáticos.*

**2. Ejecutar el Pipeline ETL:**
Puedes validar la limpieza en memoria sin tocar la base de datos:

```bash
python scripts/etl_pipeline.py --validate-only

```

Para ejecutar la carga transaccional masiva:

```bash
python scripts/etl_pipeline.py

```

*El pipeline es robusto e idempotente: valida el contrato del Excel, inyecta controles de calidad para los 18 valores nulos de `group_space`, redondea flotantes problemáticos y garantiza exactamente 96,195 hechos por ejecución.*

**3. Desplegar lógica analítica y capa semántica:**

También ejecutado con DBeaver

## Hallazgos Analíticos Principales

Para un desglose metodológico completo, consultar `docs/findings.md`.

* **Producción por lactancia:** El máximo promedio se observó entre los 31 y 60 días (Etapa *Peak*), alcanzando **2.6931 litros por control**. Posteriormente se registra un declive progresivo (ej. 1.4958 L entre los días 181 y 270).
* **Manejo Operativo:** Existen amplias diferencias descriptivas. La combinación `Group space 4 | Corral 4` lideró con 2.9668 L promedio, mientras que `Group space 3 | Corral 66` registró el mínimo con 1.1948 L. *(Nota: Diferencia sujeta a composición poblacional, no estrictamente causal)*.
* **Impacto Climático (THI):** Se identificó una correlación negativa débil pero consistente entre el índice de estrés calórico (THI) y la producción (`r = -0.2304`).
* **Cobertura Longitudinal:** El **93.46%** de las ovejas cuenta con un solo control registrado en este periodo, orientando el alcance del proyecto hacia la robustez de las tendencias agregadas por sobre las trayectorias individuales.
* **Calidad de Datos:** El **99.9813%** de los registros están perfectos. Los únicos 18 registros con datos operativos faltantes se retuvieron y mapearon hacia la etiqueta `MISSING_GROUP_SPACE` en la dimensión de calidad para garantizar cero pérdida de hechos contables.

## Tecnologías Utilizadas

* **Infraestructura de Datos:** Amazon Aurora PostgreSQL, PostgreSQL local.
* **Ingeniería ETL:** Python 3.10+, `pandas`, `SQLAlchemy`, `psycopg2`.
* **Visualización y BI:** Power BI, DAX, TMDL.
* **Control de Versiones:** Git.