# Implementación en Amazon Aurora PostgreSQL

## 1. Servicio utilizado

El modelo dimensional fue implementado directamente en un clúster de Amazon Aurora compatible con PostgreSQL.

No se utilizó una base de datos local como ambiente intermedio. Tanto la ejecución del DDL como las cargas y validaciones del ETL se realizaron contra Aurora.

## 2. Arquitectura

```text
raw_data.xlsx
      │
      ▼
scripts/etl_pipeline.py
      │
      │ SQLAlchemy + psycopg2
      ▼
Amazon Aurora PostgreSQL
├── sheep_dw
│   ├── dim_sheep
│   ├── dim_date
│   ├── dim_lactation_stage
│   ├── dim_management
│   ├── dim_weather_condition
│   ├── dim_lunar
│   ├── dim_data_quality
│   └── fact_milk_control
└── sheep_mart
    └── vistas analíticas
```

## 3. Configuración de conexión

La conexión se configura mediante variables de entorno.

```env
DB_HOST=<AURORA_CLUSTER_ENDPOINT>
DB_PORT=5432
DB_NAME=<DATABASE_NAME>
DB_USER=<DATABASE_USER>
DB_PASSWORD=<DATABASE_PASSWORD>
DB_SSLMODE=require
DB_CONNECT_TIMEOUT=20
ETL_CHUNK_SIZE=500
```

El archivo real `.env` no se incluye en el repositorio.

El repositorio contiene únicamente `.env.example` como plantilla.

## 4. Seguridad

Las siguientes medidas se utilizaron:

* Las credenciales no están escritas en el código.
* `.env` está excluido mediante `.gitignore`.
* La conexión utiliza SSL mediante `DB_SSLMODE=require`.
* El acceso de red al clúster está restringido mediante la configuración de red y seguridad de AWS.
* El endpoint, usuario y contraseña reales no se publican en la documentación.
* No se almacenan secretos en capturas de pantalla.

## 5. Esquemas

Se crearon dos esquemas:

### `sheep_dw`

Contiene el modelo dimensional atómico:

* siete dimensiones;
* una tabla de hechos;
* claves primarias;
* claves foráneas;
* restricciones de calidad;
* índices para filtros y joins.

### `sheep_mart`

Está reservado para vistas analíticas agregadas utilizadas por el dashboard.

## 6. Despliegue del modelo

El DDL se ejecuta mediante:

```bash
psql \
  -h "$DB_HOST" \
  -p "$DB_PORT" \
  -U "$DB_USER" \
  -d "$DB_NAME" \
  -v ON_ERROR_STOP=1 \
  -f scripts/01_schema_ddl.sql
```

## 7. Ejecución del ETL

Primero se puede validar la fuente sin modificar Aurora:

```bash
python scripts/etl_pipeline.py --validate-only
```

La carga completa se ejecuta mediante:

```bash
python scripts/etl_pipeline.py
```

El pipeline realiza:

1. extracción del libro de Excel;
2. validación del contrato de columnas;
3. limpieza y tipado;
4. creación de dimensiones;
5. resolución de claves sustitutas;
6. carga de la tabla de hechos;
7. validaciones posteriores;
8. commit transaccional.

## 8. Idempotencia

El pipeline puede ejecutarse nuevamente sin duplicar datos.

En cada ejecución completa:

1. se inicia una transacción;
2. se vacían las tablas dinámicas;
3. se cargan nuevamente las dimensiones;
4. se cargan los 96,195 hechos;
5. se ejecutan validaciones;
6. se confirma la transacción únicamente si todas las validaciones pasan.

Después de dos ejecuciones, la tabla de hechos permaneció con:

```text
96,195 filas
```

## 9. Resultados de la carga

| Tabla                   |  Filas |
| ----------------------- | -----: |
| `dim_data_quality`      |      2 |
| `dim_date`              |    654 |
| `dim_lactation_stage`   |      8 |
| `dim_lunar`             |     35 |
| `dim_management`        |     12 |
| `dim_sheep`             | 13,829 |
| `dim_weather_condition` |     14 |
| `fact_milk_control`     | 96,195 |

## 10. Validaciones principales

* 96,195 filas de hechos.
* 96,195 valores únicos de `source_row_number`.
* 13,829 ovejas.
* 96,177 observaciones completas.
* 18 observaciones con espacio de grupo faltante.
* Cero balances inválidos de producción.
* Cero duplicados después de reejecutar el ETL.
* Integridad referencial validada dentro de Aurora.

## 11. Evidencia

Las capturas deben ocultar:

* endpoint completo;
* contraseña;
* usuario sensible;
* número de cuenta AWS;
* identificadores internos innecesarios.

Las evidencias recomendadas son:

1. clúster Aurora disponible en AWS;
2. esquemas `sheep_dw` y `sheep_mart`;
3. listado de tablas;
4. conteo de 96,195 hechos;
5. resultado de validación de integridad;
6. log exitoso del ETL.
