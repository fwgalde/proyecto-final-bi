# Diseño dimensional

## 1. Nombre del proyecto

**Data Warehouse para el análisis de producción lechera ovina según lactación, clima y manejo**

## 2. Problema analítico

La producción de leche registrada para una oveja puede variar según su momento dentro de la lactación, el corral y espacio de grupo asignados, y las condiciones ambientales presentes tanto el día del control como el día anterior.

Los datos originales se encuentran en un libro de Excel con observaciones de producción, fechas de parto y control, información de manejo, clima, precipitación, viento y calendario lunar. Aunque el proyecto original fue utilizado para tareas de ciencia de datos, esta entrega reorganiza la información como una solución de Business Intelligence descriptiva y reproducible.

## 3. Pregunta analítica principal

> ¿Cómo varía la producción total de leche registrada por control según los días en lactación, las condiciones climáticas del día y del día anterior, el corral y el espacio de grupo?

## 4. Preguntas secundarias

1. ¿Cómo cambia la producción promedio a medida que avanzan los días en lactación?
2. ¿Qué corrales y combinaciones de manejo registran mayor o menor producción promedio?
3. ¿Cómo se relacionan el índice temperatura-humedad, la temperatura, la humedad y la precipitación con la producción?
4. ¿Las condiciones ambientales del día anterior muestran patrones diferentes a las del día del control?
5. ¿Cómo evoluciona la producción a través del periodo observado?
6. ¿Cuántas observaciones presentan información incompleta de manejo?
7. ¿Qué ovejas presentan suficientes observaciones para analizar su evolución longitudinal?

## 5. Fuentes utilizadas

### Hoja `Hoja1`

Fuente principal de la tabla de hechos. Contiene 96,195 observaciones y 57 columnas.

### Hoja `CODIGOS ANIMALES`

Lookup auxiliar de la dimensión de ovejas. Se utilizarán:

* `Nº de Oveja` como identificador natural.
* `O` como código anonimizado para visualización.

### Hojas excluidas

No se utilizarán `DATOS SELECCIONADOS`, `FORMULAS R`, `FORMULAS R WOOD` ni `FORMULAS R WILMINK`, porque son proyecciones o artefactos derivados del modelado anterior y no representan nuevas fuentes de hechos.

## 6. Proceso de negocio

El proceso modelado es el registro y análisis de controles de producción lechera ovina.

Cada observación combina:

* una oveja;
* una fecha de control;
* una fecha de parto;
* producción matutina;
* producción vespertina;
* producción total;
* días transcurridos desde el parto;
* contexto de manejo;
* condiciones climáticas del día;
* condiciones climáticas del día anterior;
* información lunar.

## 7. Grano de la tabla de hechos

> Una fila de `fact_milk_control` representa una observación individual registrada en una fila de la hoja `Hoja1`.

El grano no se define únicamente mediante oveja, fecha de parto y fecha de control porque existe al menos una combinación repetida con valores distintos de producción y manejo.

Cada observación conservará un campo `source_row_number`, correspondiente al número físico de fila del Excel, para asegurar unicidad y trazabilidad.

## 8. Tipo de modelo

Se utilizará un esquema estrella.

La tabla central será:

* `fact_milk_control`

Las dimensiones serán:

* `dim_sheep`
* `dim_date`
* `dim_lactation_stage`
* `dim_management`
* `dim_weather_condition`
* `dim_lunar`
* `dim_data_quality`

## 9. Dimensiones de rol

### `dim_date`

La misma dimensión se reutilizará en dos roles:

* `control_date_key`: fecha en que se registró el control.
* `lambing_date_key`: fecha de parto de la oveja.

No se creará una dimensión distinta para cada tipo de fecha.

### `dim_weather_condition`

La dimensión se reutilizará en dos roles:

* `current_weather_condition_key`
* `previous_weather_condition_key`

Esta dimensión almacenará los códigos categóricos proporcionados por la fuente para velocidad del viento y precipitación. Las mediciones continuas permanecerán en la tabla de hechos.

### `dim_lunar`

La dimensión se reutilizará en dos roles:

* `current_lunar_key`
* `previous_lunar_key`

## 10. Diseño de dimensiones

### `dim_sheep`

Representa la identidad relativamente estática del animal.

Atributos:

* `sheep_key`: clave sustituta.
* `sheep_id`: clave natural proveniente de `Nº de Oveja`.
* `animal_code`: código anonimizado proveniente de la columna `O` de `CODIGOS ANIMALES`.

No se almacenará `observation_count` en esta dimensión. Ese conteo se calculará a partir de la tabla de hechos.

### `dim_date`

Calendario reutilizable para fechas de control y parto.

Atributos:

* `date_key`
* `full_date`
* `year`
* `quarter`
* `month`
* `month_name`
* `week_of_year`
* `day_of_month`
* `day_of_year`
* `day_of_week`
* `day_name`
* `is_weekend`

### `dim_lactation_stage`

Catálogo estático de periodos analíticos de lactación.

Atributos:

* `lactation_stage_key`
* `stage_code`
* `stage_label`
* `min_days_in_milk`
* `max_days_in_milk`
* `stage_order`

Los periodos se utilizarán como agrupaciones operativas para el dashboard. No se interpretarán automáticamente como etapas biológicas causales.

Periodos iniciales:

| Orden | Código      | Rango          |
| ----: | ----------- | -------------- |
|     1 | `D000_030`  | 0–30 días      |
|     2 | `D031_060`  | 31–60 días     |
|     3 | `D061_090`  | 61–90 días     |
|     4 | `D091_120`  | 91–120 días    |
|     5 | `D121_180`  | 121–180 días   |
|     6 | `D181_270`  | 181–270 días   |
|     7 | `D271_365`  | 271–365 días   |
|     8 | `D366_PLUS` | 366 días o más |

### `dim_management`

Representa el contexto de manejo observado al momento del control.

Atributos:

* `management_key`
* `group_space_code`
* `group_space_label`
* `pen_id`
* `management_natural_key`

La clave natural será la combinación de espacio de grupo y corral.

Para los 18 registros sin espacio de grupo:

* `group_space_code = -1`
* `group_space_label = Unknown`

Se conservará el corral disponible.

### `dim_weather_condition`

Catálogo de condiciones ambientales categóricas.

Atributos:

* `weather_condition_key`
* `wind_speed_category`
* `precipitation_category`
* `weather_natural_key`

Será reutilizada para las condiciones del día del control y del día anterior.

Las variables continuas —temperatura, humedad, THI, viento, radiación y precipitación— se almacenarán como medidas de la tabla de hechos.

### `dim_lunar`

Catálogo de contexto lunar.

Atributos:

* `lunar_key`
* `lunar_phase`
* `lunar_phase_index`
* `lunar_natural_key`

Será reutilizada para el día del control y el día anterior.

### `dim_data_quality`

Dimensión pequeña de calidad del registro.

Atributos:

* `data_quality_key`
* `quality_code`
* `quality_label`
* `has_missing_group_space`

Códigos iniciales:

* `COMPLETE`
* `MISSING_GROUP_SPACE`

## 11. Tabla de hechos

### `fact_milk_control`

Claves:

* `milk_control_key`
* `source_row_number`
* `sheep_key`
* `control_date_key`
* `lambing_date_key`
* `lactation_stage_key`
* `management_key`
* `current_weather_condition_key`
* `previous_weather_condition_key`
* `current_lunar_key`
* `previous_lunar_key`
* `data_quality_key`

Medidas productivas:

* `morning_milking_liters`
* `afternoon_milking_liters`
* `total_milk_liters`
* `days_in_milk`

Medidas climáticas del día del control:

* `avg_temp_c`
* `max_temp_c`
* `min_temp_c`
* `avg_humidity_pct`
* `max_humidity_pct`
* `min_humidity_pct`
* `thi`
* `wind_speed_mps`
* `wind_direction_deg`
* `max_wind_speed_mps`
* `max_wind_direction_deg`
* `radiation_mj_m2`
* `precipitation_mm`

Medidas climáticas del día anterior:

* `avg_temp_c_previous_day`
* `max_temp_c_previous_day`
* `min_temp_c_previous_day`
* `avg_humidity_pct_previous_day`
* `max_humidity_pct_previous_day`
* `min_humidity_pct_previous_day`
* `thi_previous_day`
* `wind_speed_mps_previous_day`
* `wind_direction_deg_previous_day`
* `max_wind_speed_mps_previous_day`
* `max_wind_direction_deg_previous_day`
* `radiation_mj_m2_previous_day`
* `precipitation_mm_previous_day`

## 12. Medidas aditivas y no aditivas

### Aditivas a través de observaciones

* `morning_milking_liters`
* `afternoon_milking_liters`
* `total_milk_liters`
* `precipitation_mm`, cuando la agregación temporal sea conceptualmente apropiada

### No aditivas

No deben sumarse entre observaciones:

* `days_in_milk`
* temperaturas
* humedad
* THI
* velocidad y dirección del viento
* radiación cuando se compare como condición promedio

Estas medidas se analizarán principalmente con:

* promedio;
* mediana;
* mínimo;
* máximo;
* desviación estándar;
* percentiles.

## 13. Reglas de calidad verificadas

El ETL validará:

1. `total_milk_liters = morning_milking_liters + afternoon_milking_liters`.
2. `days_in_milk = control_date - lambing_date`.
3. `lambing_month = month(lambing_date)`.
4. `weather_date = control_date`.
5. `date_before_control = control_date - 1 día`.
6. `previous_weather_date = control_date - 1 día`.
7. `total_milk_liters >= 0`.
8. Las claves foráneas de la tabla de hechos tienen correspondencia en sus dimensiones.
9. `source_row_number` es único.
10. La cantidad de filas cargadas en la tabla de hechos coincide con las 96,195 filas de origen.

## 14. Tratamiento de valores faltantes

No se eliminarán las 18 observaciones con `Espacio grupo` nulo.

Se asignará:

* código de espacio `-1`;
* etiqueta `Unknown`;
* calidad `MISSING_GROUP_SPACE`.

Esto permite conservar la producción y el resto del contexto válido del registro.

## 15. Columnas fuente que no se cargarán directamente

No se cargarán como columnas independientes:

* `Mes de parto`, porque se deriva de `Fecha Parto`.
* `Fecha Clima`, porque coincide con `Fecha control`.
* `Dia antes del control`, porque equivale a `Fecha control - 1`.
* La segunda fecha climática, porque equivale a `Fecha control - 1`.
* Las horas de máximos y mínimos climáticos, porque no forman parte de las preguntas analíticas del MVP.
* Los códigos `WOOD` y `WILMINK`, porque corresponden a artefactos del modelado matemático anterior.

Estas decisiones reducen redundancia sin perder la capacidad de responder las preguntas del proyecto.

## 16. Limitaciones analíticas

* El análisis será descriptivo y exploratorio.
* Una asociación observada no implica causalidad.
* Los periodos de lactación son agrupaciones operativas.
* No se dispone de atributos biológicos adicionales como raza, edad, número de parto o estado de salud.
* La cantidad de observaciones por oveja es muy desigual.
* Una gran proporción de ovejas tiene una sola observación, por lo que el análisis longitudinal individual debe filtrar animales con múltiples controles.
