# Diccionario de datos

## 1. Fuentes

| Hoja                  | Uso                                    |
| --------------------- | -------------------------------------- |
| `Hoja1`               | Fuente principal de observaciones      |
| `CODIGOS ANIMALES`    | Lookup de código anonimizado por oveja |
| `DATOS SELECCIONADOS` | Excluida por redundancia               |
| `FORMULAS R`          | Excluida                               |
| `FORMULAS R WOOD`     | Excluida                               |
| `FORMULAS R WILMINK`  | Excluida                               |

## 2. Identidad, fechas, producción y manejo

| Columna original     | Columna limpia             | Destino             | Regla                           |
| -------------------- | -------------------------- | ------------------- | ------------------------------- |
| `Nº de Oveja`        | `sheep_id`                 | `dim_sheep`         | Clave natural                   |
| `O`                  | `animal_code`              | `dim_sheep`         | Lookup desde `CODIGOS ANIMALES` |
| `Fecha Parto`        | `lambing_date`             | `dim_date`          | Genera `lambing_date_key`       |
| `Fecha control`      | `control_date`             | `dim_date`          | Genera `control_date_key`       |
| `Ordeño mañana(lts)` | `morning_milking_liters`   | `fact_milk_control` | NUMERIC                         |
| `Ordeño tarde(lts)`  | `afternoon_milking_liters` | `fact_milk_control` | NUMERIC                         |
| `Leche Total`        | `total_milk_liters`        | `fact_milk_control` | Debe ser mañana + tarde         |
| `Dias ordeño `       | `days_in_milk`             | `fact_milk_control` | Debe ser control - parto        |
| `Espacio grupo`      | `group_space_code`         | `dim_management`    | Nulo se convierte en -1         |
| `Parque(Corral)`     | `pen_id`                   | `dim_management`    | Parte de clave natural          |
| `Mes de parto`       | `lambing_month_source`     | No se carga         | Se valida contra fecha de parto |

## 3. Clima del día del control

| Columna original              | Columna limpia           | Destino                                 |
| ----------------------------- | ------------------------ | --------------------------------------- |
| `Temp, media(ºC)`             | `avg_temp_c`             | `fact_milk_control`                     |
| `Temp, max(ºC)`               | `max_temp_c`             | `fact_milk_control`                     |
| `Temp, min(ºC)`               | `min_temp_c`             | `fact_milk_control`                     |
| `Hum, med(%)`                 | `avg_humidity_pct`       | `fact_milk_control`                     |
| `Humedad max(%)`              | `max_humidity_pct`       | `fact_milk_control`                     |
| `Humedad min(%)`              | `min_humidity_pct`       | `fact_milk_control`                     |
| `THI`                         | `thi`                    | `fact_milk_control`                     |
| `Vel, viento(m/s)`            | `wind_speed_mps`         | `fact_milk_control`                     |
| `Dir, viento (º)`             | `wind_direction_deg`     | `fact_milk_control`                     |
| `Vel, max(m/s)`               | `max_wind_speed_mps`     | `fact_milk_control`                     |
| `Dir, Vel, max (º)`           | `max_wind_direction_deg` | `fact_milk_control`                     |
| `Radiacion(MJ/m^2)`           | `radiation_mj_m2`        | `fact_milk_control`                     |
| `Precipitacion(mm)`           | `precipitation_mm`       | `fact_milk_control`                     |
| `Clasificacion velocidad`     | `wind_speed_category`    | `dim_weather_condition`                 |
| `Clasificacion precipitacion` | `precipitation_category` | `dim_weather_condition`                 |
| `Calendario lunar`            | `lunar_phase`            | `dim_lunar`                             |
| `Clasif. Cal. lunar`          | `lunar_phase_index`      | `dim_lunar`                             |
| `Fecha Clima`                 | `weather_date_source`    | No se carga; debe coincidir con control |

## 4. Clima del día anterior

Debido a encabezados repetidos en Excel, el ETL no dependerá de los sufijos automáticos de pandas. Las columnas se nombrarán explícitamente por posición.

| Concepto original                       | Columna limpia                        | Destino                           |
| --------------------------------------- | ------------------------------------- | --------------------------------- |
| Temperatura media anterior              | `avg_temp_c_previous_day`             | `fact_milk_control`               |
| Temperatura máxima anterior             | `max_temp_c_previous_day`             | `fact_milk_control`               |
| Temperatura mínima anterior             | `min_temp_c_previous_day`             | `fact_milk_control`               |
| Humedad media anterior                  | `avg_humidity_pct_previous_day`       | `fact_milk_control`               |
| Humedad máxima anterior                 | `max_humidity_pct_previous_day`       | `fact_milk_control`               |
| Humedad mínima anterior                 | `min_humidity_pct_previous_day`       | `fact_milk_control`               |
| `ITH Ant`                               | `thi_previous_day`                    | `fact_milk_control`               |
| Velocidad media anterior                | `wind_speed_mps_previous_day`         | `fact_milk_control`               |
| Dirección del viento anterior           | `wind_direction_deg_previous_day`     | `fact_milk_control`               |
| Velocidad máxima anterior               | `max_wind_speed_mps_previous_day`     | `fact_milk_control`               |
| Dirección de velocidad máxima anterior  | `max_wind_direction_deg_previous_day` | `fact_milk_control`               |
| Radiación anterior                      | `radiation_mj_m2_previous_day`        | `fact_milk_control`               |
| Precipitación anterior                  | `precipitation_mm_previous_day`       | `fact_milk_control`               |
| Clasificación de velocidad anterior     | `wind_speed_category_previous_day`    | `dim_weather_condition`           |
| Clasificación de precipitación anterior | `precipitation_category_previous_day` | `dim_weather_condition`           |
| Calendario lunar anterior               | `lunar_phase_previous_day`            | `dim_lunar`                       |
| Clasificación lunar anterior            | `lunar_phase_index_previous_day`      | `dim_lunar`                       |
| Fecha anterior                          | `previous_weather_date_source`        | No se carga; debe ser control - 1 |

## 5. Campos técnicos creados por el ETL

| Campo                            | Destino             | Descripción                        |
| -------------------------------- | ------------------- | ---------------------------------- |
| `source_row_number`              | `fact_milk_control` | Número físico de fila en `Hoja1`   |
| `milk_control_key`               | `fact_milk_control` | Clave sustituta                    |
| `sheep_key`                      | Fact/dimensión      | FK a `dim_sheep`                   |
| `control_date_key`               | Fact/dimensión      | FK a `dim_date`                    |
| `lambing_date_key`               | Fact/dimensión      | FK a `dim_date`                    |
| `lactation_stage_key`            | Fact/dimensión      | Periodo derivado de `days_in_milk` |
| `management_key`                 | Fact/dimensión      | Combinación de espacio y corral    |
| `current_weather_condition_key`  | Fact/dimensión      | Categorías climáticas actuales     |
| `previous_weather_condition_key` | Fact/dimensión      | Categorías climáticas anteriores   |
| `current_lunar_key`              | Fact/dimensión      | Contexto lunar actual              |
| `previous_lunar_key`             | Fact/dimensión      | Contexto lunar anterior            |
| `data_quality_key`               | Fact/dimensión      | Calidad del registro               |

## 6. Rangos observados para validación

| Campo                      | Mínimo | Máximo |
| -------------------------- | -----: | -----: |
| `morning_milking_liters`   |   0.00 |   4.72 |
| `afternoon_milking_liters` |   0.00 |   4.42 |
| `total_milk_liters`        |   0.10 |   6.69 |
| `days_in_milk`             |     13 |    653 |
| `avg_temp_c`               |   1.92 |  23.20 |
| `max_temp_c`               |   7.37 |  32.50 |
| `min_temp_c`               |  -5.81 |  13.02 |
| `avg_humidity_pct`         |  48.09 |  95.70 |
| `max_humidity_pct`         |  83.50 | 100.00 |
| `min_humidity_pct`         |  14.07 |  81.10 |
| `thi`                      | 45.366 | 87.597 |
| `wind_speed_mps`           |   0.94 |   5.84 |
| `max_wind_speed_mps`       |   2.99 |  13.78 |
| `radiation_mj_m2`          |   4.89 |  31.44 |
| `precipitation_mm`         |   0.00 |  29.49 |

Estos rangos describen el archivo actual. No deben convertirse automáticamente en límites científicos universales.

## 7. Columnas de hora excluidas del MVP

Se conservarán en el archivo crudo, pero no se cargarán inicialmente:

* hora de temperatura máxima;
* hora de temperatura mínima;
* hora de humedad máxima;
* hora de humedad mínima;
* hora de velocidad máxima;
* equivalentes del día anterior.

La exclusión se debe a que no responden directamente las preguntas analíticas prioritarias del dashboard.
