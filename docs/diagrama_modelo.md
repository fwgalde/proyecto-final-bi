# Diagrama del modelo dimensional

## Grano

Una fila de `fact_milk_control` representa una observación individual registrada en una fila de la hoja `Hoja1`.

```mermaid
erDiagram
    DIM_SHEEP ||--o{ FACT_MILK_CONTROL : "sheep_key"

    DIM_DATE ||--o{ FACT_MILK_CONTROL : "control_date_key"
    DIM_DATE ||--o{ FACT_MILK_CONTROL : "lambing_date_key"

    DIM_LACTATION_STAGE ||--o{ FACT_MILK_CONTROL : "lactation_stage_key"
    DIM_MANAGEMENT ||--o{ FACT_MILK_CONTROL : "management_key"

    DIM_WEATHER_CONDITION ||--o{ FACT_MILK_CONTROL : "current_weather_condition_key"
    DIM_WEATHER_CONDITION ||--o{ FACT_MILK_CONTROL : "previous_weather_condition_key"

    DIM_LUNAR ||--o{ FACT_MILK_CONTROL : "current_lunar_key"
    DIM_LUNAR ||--o{ FACT_MILK_CONTROL : "previous_lunar_key"

    DIM_DATA_QUALITY ||--o{ FACT_MILK_CONTROL : "data_quality_key"

    DIM_SHEEP {
        int sheep_key PK
        bigint sheep_id UK
        varchar animal_code
    }

    DIM_DATE {
        int date_key PK
        date full_date UK
        smallint year
        smallint quarter
        smallint month
        varchar month_name
        smallint week_of_year
        smallint day_of_month
        smallint day_of_year
        smallint day_of_week
        varchar day_name
        boolean is_weekend
    }

    DIM_LACTATION_STAGE {
        smallint lactation_stage_key PK
        varchar stage_code UK
        varchar stage_label
        int min_days_in_milk
        int max_days_in_milk
        smallint stage_order
    }

    DIM_MANAGEMENT {
        int management_key PK
        smallint group_space_code
        varchar group_space_label
        smallint pen_id
        varchar management_natural_key UK
    }

    DIM_WEATHER_CONDITION {
        int weather_condition_key PK
        smallint wind_speed_category
        smallint precipitation_category
        varchar weather_natural_key UK
    }

    DIM_LUNAR {
        int lunar_key PK
        varchar lunar_phase
        smallint lunar_phase_index
        varchar lunar_natural_key UK
    }

    DIM_DATA_QUALITY {
        smallint data_quality_key PK
        varchar quality_code UK
        varchar quality_label
        boolean has_missing_group_space
    }

    FACT_MILK_CONTROL {
        bigint milk_control_key PK
        int source_row_number UK

        int sheep_key FK
        int control_date_key FK
        int lambing_date_key FK
        smallint lactation_stage_key FK
        int management_key FK

        int current_weather_condition_key FK
        int previous_weather_condition_key FK
        int current_lunar_key FK
        int previous_lunar_key FK
        smallint data_quality_key FK

        numeric morning_milking_liters
        numeric afternoon_milking_liters
        numeric total_milk_liters
        int days_in_milk

        numeric avg_temp_c
        numeric max_temp_c
        numeric min_temp_c
        numeric avg_humidity_pct
        numeric max_humidity_pct
        numeric min_humidity_pct
        numeric thi
        numeric wind_speed_mps
        numeric wind_direction_deg
        numeric max_wind_speed_mps
        numeric max_wind_direction_deg
        numeric radiation_mj_m2
        numeric precipitation_mm

        numeric avg_temp_c_previous_day
        numeric max_temp_c_previous_day
        numeric min_temp_c_previous_day
        numeric avg_humidity_pct_previous_day
        numeric max_humidity_pct_previous_day
        numeric min_humidity_pct_previous_day
        numeric thi_previous_day
        numeric wind_speed_mps_previous_day
        numeric wind_direction_deg_previous_day
        numeric max_wind_speed_mps_previous_day
        numeric max_wind_direction_deg_previous_day
        numeric radiation_mj_m2_previous_day
        numeric precipitation_mm_previous_day
    }
```

## Dimensiones reutilizadas por rol

* `DIM_DATE` se utiliza como fecha de control y fecha de parto.
* `DIM_WEATHER_CONDITION` se utiliza para el día del control y el día anterior.
* `DIM_LUNAR` se utiliza para el día del control y el día anterior.

## Nota sobre cardinalidad

Las dimensiones contienen descripciones relativamente estáticas o catálogos de contexto. Las medidas repetibles y los eventos se concentran en `FACT_MILK_CONTROL`.
