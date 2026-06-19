/*
===============================================================================
PROJECT:
    Data Warehouse for Dairy Sheep Milk Production Analysis

FILE:
    scripts/03_views_dashboard.sql

PURPOSE:
    Create a semantic star schema specifically designed for Power BI.

DESIGN PRINCIPLES:
    - Keep one atomic fact table.
    - Expose clean and stable semantic views.
    - Duplicate role-playing dimensions as separate views so that all
      Power BI relationships can remain active.
    - Keep aggregation logic primarily in Power BI measures.
    - Avoid unnecessary flattened tables and duplicated facts.

POWER BI RECOMMENDATION:
    Load only the sheep_mart.pbi_* views.
===============================================================================
*/

BEGIN;

CREATE SCHEMA IF NOT EXISTS sheep_mart;


-- ============================================================================
-- 1. SHEEP DIMENSION
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_sheep AS
SELECT
    sheep_key,
    sheep_id,
    animal_code
FROM sheep_dw.dim_sheep;

COMMENT ON VIEW sheep_mart.pbi_dim_sheep IS
    'Power BI sheep dimension. One row per sheep.';


-- ============================================================================
-- 2. CONTROL-DATE DIMENSION
-- ============================================================================
-- Separate Power BI view of dim_date.
-- This relationship can remain active:
--   pbi_dim_control_date[control_date_key]
--       1 ──── * pbi_fact_milk_control[control_date_key]
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_control_date AS
SELECT
    date_key AS control_date_key,
    full_date AS control_date,

    year AS control_year,
    quarter AS control_quarter,
    month AS control_month_number,
    month_name AS control_month_name,
    week_of_year AS control_week_of_year,
    day_of_month AS control_day_of_month,
    day_of_year AS control_day_of_year,
    day_of_week AS control_day_of_week,
    day_name AS control_day_name,
    is_weekend AS control_is_weekend,

    TO_CHAR(
        full_date,
        'YYYY-MM'
    ) AS control_year_month,

    year * 100 + month AS control_year_month_sort

FROM sheep_dw.dim_date;

COMMENT ON VIEW sheep_mart.pbi_dim_control_date IS
    'Role-playing Power BI date dimension for milk-control dates.';


-- ============================================================================
-- 3. LAMBING-DATE DIMENSION
-- ============================================================================
-- Separate logical table in Power BI.
-- This avoids an inactive second relationship to one shared date table.
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_lambing_date AS
SELECT
    date_key AS lambing_date_key,
    full_date AS lambing_date,

    year AS lambing_year,
    quarter AS lambing_quarter,
    month AS lambing_month_number,
    month_name AS lambing_month_name,
    week_of_year AS lambing_week_of_year,
    day_of_month AS lambing_day_of_month,
    day_of_year AS lambing_day_of_year,
    day_of_week AS lambing_day_of_week,
    day_name AS lambing_day_name,
    is_weekend AS lambing_is_weekend,

    TO_CHAR(
        full_date,
        'YYYY-MM'
    ) AS lambing_year_month,

    year * 100 + month AS lambing_year_month_sort

FROM sheep_dw.dim_date;

COMMENT ON VIEW sheep_mart.pbi_dim_lambing_date IS
    'Role-playing Power BI date dimension for lambing dates.';


-- ============================================================================
-- 4. LACTATION-STAGE DIMENSION
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_lactation_stage AS
SELECT
    lactation_stage_key,
    stage_code,
    stage_label,
    min_days_in_milk,
    max_days_in_milk,
    stage_order
FROM sheep_dw.dim_lactation_stage;

COMMENT ON VIEW sheep_mart.pbi_dim_lactation_stage IS
    'Power BI catalog of operational days-in-milk ranges.';


-- ============================================================================
-- 5. MANAGEMENT DIMENSION
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_management AS
SELECT
    management_key,
    group_space_code,
    group_space_label,
    pen_id,
    management_natural_key,

    CONCAT(
        'Pen ',
        pen_id
    ) AS pen_label,

    CONCAT(
        group_space_label,
        ' | Pen ',
        pen_id
    ) AS management_label

FROM sheep_dw.dim_management;

COMMENT ON VIEW sheep_mart.pbi_dim_management IS
    'Power BI management dimension: group-space and pen combination.';


-- ============================================================================
-- 6. CURRENT-WEATHER DIMENSION
-- ============================================================================
-- Separate view to support an active current-weather relationship.
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_current_weather_condition AS
SELECT
    weather_condition_key AS current_weather_condition_key,

    wind_speed_category AS current_wind_speed_category,
    precipitation_category AS current_precipitation_category,

    weather_natural_key AS current_weather_natural_key,

    CONCAT(
        'Wind category ',
        wind_speed_category,
        ' | Precipitation category ',
        precipitation_category
    ) AS current_weather_category_label

FROM sheep_dw.dim_weather_condition;

COMMENT ON VIEW sheep_mart.pbi_dim_current_weather_condition IS
    'Role-playing Power BI dimension for current-day weather categories.';


-- ============================================================================
-- 7. PREVIOUS-DAY WEATHER DIMENSION
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_previous_weather_condition AS
SELECT
    weather_condition_key AS previous_weather_condition_key,

    wind_speed_category AS previous_wind_speed_category,
    precipitation_category AS previous_precipitation_category,

    weather_natural_key AS previous_weather_natural_key,

    CONCAT(
        'Wind category ',
        wind_speed_category,
        ' | Precipitation category ',
        precipitation_category
    ) AS previous_weather_category_label

FROM sheep_dw.dim_weather_condition;

COMMENT ON VIEW sheep_mart.pbi_dim_previous_weather_condition IS
    'Role-playing Power BI dimension for previous-day weather categories.';


-- ============================================================================
-- 8. CURRENT-LUNAR DIMENSION
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_current_lunar AS
SELECT
    lunar_key AS current_lunar_key,
    lunar_phase AS current_lunar_phase,
    lunar_phase_index AS current_lunar_phase_index,
    lunar_natural_key AS current_lunar_natural_key
FROM sheep_dw.dim_lunar;

COMMENT ON VIEW sheep_mart.pbi_dim_current_lunar IS
    'Role-playing Power BI lunar dimension for the control day.';


-- ============================================================================
-- 9. PREVIOUS-DAY LUNAR DIMENSION
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_previous_lunar AS
SELECT
    lunar_key AS previous_lunar_key,
    lunar_phase AS previous_lunar_phase,
    lunar_phase_index AS previous_lunar_phase_index,
    lunar_natural_key AS previous_lunar_natural_key
FROM sheep_dw.dim_lunar;

COMMENT ON VIEW sheep_mart.pbi_dim_previous_lunar IS
    'Role-playing Power BI lunar dimension for the previous day.';


-- ============================================================================
-- 10. DATA-QUALITY DIMENSION
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_dim_data_quality AS
SELECT
    data_quality_key,
    quality_code,
    quality_label,
    has_missing_group_space
FROM sheep_dw.dim_data_quality;

COMMENT ON VIEW sheep_mart.pbi_dim_data_quality IS
    'Power BI data-quality dimension.';


-- ============================================================================
-- 11. ATOMIC FACT VIEW FOR POWER BI
-- ============================================================================
-- This remains at the exact warehouse grain:
-- one source observation per row.
--
-- Row-level analytical deltas are added because they are stable,
-- reusable measures and avoid repetitive calculated columns in Power BI.
-- ============================================================================

CREATE OR REPLACE VIEW sheep_mart.pbi_fact_milk_control AS
SELECT
    f.milk_control_key,
    f.source_row_number,

    -- Foreign keys
    f.sheep_key,
    f.control_date_key,
    f.lambing_date_key,
    f.lactation_stage_key,
    f.management_key,

    f.current_weather_condition_key,
    f.previous_weather_condition_key,

    f.current_lunar_key,
    f.previous_lunar_key,

    f.data_quality_key,

    -- Production measures
    f.morning_milking_liters,
    f.afternoon_milking_liters,
    f.total_milk_liters,
    f.days_in_milk,

    CASE
        WHEN f.total_milk_liters = 0 THEN NULL
        ELSE
            f.morning_milking_liters
            / f.total_milk_liters
    END AS morning_milk_share,

    CASE
        WHEN f.total_milk_liters = 0 THEN NULL
        ELSE
            f.afternoon_milking_liters
            / f.total_milk_liters
    END AS afternoon_milk_share,

    -- Current-day weather
    f.avg_temp_c,
    f.max_temp_c,
    f.min_temp_c,

    f.avg_humidity_pct,
    f.max_humidity_pct,
    f.min_humidity_pct,

    f.thi,

    f.wind_speed_mps,
    f.wind_direction_deg,
    f.max_wind_speed_mps,
    f.max_wind_direction_deg,

    f.radiation_mj_m2,
    f.precipitation_mm,

    -- Previous-day weather
    f.avg_temp_c_previous_day,
    f.max_temp_c_previous_day,
    f.min_temp_c_previous_day,

    f.avg_humidity_pct_previous_day,
    f.max_humidity_pct_previous_day,
    f.min_humidity_pct_previous_day,

    f.thi_previous_day,

    f.wind_speed_mps_previous_day,
    f.wind_direction_deg_previous_day,
    f.max_wind_speed_mps_previous_day,
    f.max_wind_direction_deg_previous_day,

    f.radiation_mj_m2_previous_day,
    f.precipitation_mm_previous_day,

    -- Day-over-day analytical deltas
    f.avg_temp_c
        - f.avg_temp_c_previous_day
        AS avg_temp_change_vs_previous_day,

    f.avg_humidity_pct
        - f.avg_humidity_pct_previous_day
        AS avg_humidity_change_vs_previous_day,

    f.thi
        - f.thi_previous_day
        AS thi_change_vs_previous_day,

    f.precipitation_mm
        - f.precipitation_mm_previous_day
        AS precipitation_change_vs_previous_day,

    f.radiation_mj_m2
        - f.radiation_mj_m2_previous_day
        AS radiation_change_vs_previous_day

FROM sheep_dw.fact_milk_control AS f;

COMMENT ON VIEW sheep_mart.pbi_fact_milk_control IS
    'Atomic Power BI fact view with production, weather and day-over-day deltas.';


COMMIT;


/*
===============================================================================
POST-DEPLOYMENT VALIDATION
===============================================================================

-- List Power BI semantic views
SELECT
    table_schema,
    table_name
FROM information_schema.views
WHERE table_schema = 'sheep_mart'
  AND table_name LIKE 'pbi_%'
ORDER BY table_name;


-- The Power BI fact view must retain the atomic grain
SELECT
    COUNT(*) AS fact_rows,
    COUNT(DISTINCT milk_control_key) AS unique_fact_keys,
    COUNT(DISTINCT source_row_number) AS unique_source_rows
FROM sheep_mart.pbi_fact_milk_control;


-- Expected:
-- fact_rows         = 96195
-- unique_fact_keys  = 96195
-- unique_source_rows= 96195


-- Check every Power BI fact FK has a matching role-playing dimension row
SELECT
    COUNT(*) FILTER (
        WHERE s.sheep_key IS NULL
    ) AS missing_sheep,

    COUNT(*) FILTER (
        WHERE cd.control_date_key IS NULL
    ) AS missing_control_date,

    COUNT(*) FILTER (
        WHERE ld.lambing_date_key IS NULL
    ) AS missing_lambing_date,

    COUNT(*) FILTER (
        WHERE ls.lactation_stage_key IS NULL
    ) AS missing_lactation_stage,

    COUNT(*) FILTER (
        WHERE m.management_key IS NULL
    ) AS missing_management,

    COUNT(*) FILTER (
        WHERE cw.current_weather_condition_key IS NULL
    ) AS missing_current_weather,

    COUNT(*) FILTER (
        WHERE pw.previous_weather_condition_key IS NULL
    ) AS missing_previous_weather,

    COUNT(*) FILTER (
        WHERE cl.current_lunar_key IS NULL
    ) AS missing_current_lunar,

    COUNT(*) FILTER (
        WHERE pl.previous_lunar_key IS NULL
    ) AS missing_previous_lunar,

    COUNT(*) FILTER (
        WHERE q.data_quality_key IS NULL
    ) AS missing_quality

FROM sheep_mart.pbi_fact_milk_control AS f

LEFT JOIN sheep_mart.pbi_dim_sheep AS s
  ON s.sheep_key = f.sheep_key

LEFT JOIN sheep_mart.pbi_dim_control_date AS cd
  ON cd.control_date_key = f.control_date_key

LEFT JOIN sheep_mart.pbi_dim_lambing_date AS ld
  ON ld.lambing_date_key = f.lambing_date_key

LEFT JOIN sheep_mart.pbi_dim_lactation_stage AS ls
  ON ls.lactation_stage_key = f.lactation_stage_key

LEFT JOIN sheep_mart.pbi_dim_management AS m
  ON m.management_key = f.management_key

LEFT JOIN sheep_mart.pbi_dim_current_weather_condition AS cw
  ON cw.current_weather_condition_key =
     f.current_weather_condition_key

LEFT JOIN sheep_mart.pbi_dim_previous_weather_condition AS pw
  ON pw.previous_weather_condition_key =
     f.previous_weather_condition_key

LEFT JOIN sheep_mart.pbi_dim_current_lunar AS cl
  ON cl.current_lunar_key = f.current_lunar_key

LEFT JOIN sheep_mart.pbi_dim_previous_lunar AS pl
  ON pl.previous_lunar_key = f.previous_lunar_key

LEFT JOIN sheep_mart.pbi_dim_data_quality AS q
  ON q.data_quality_key = f.data_quality_key;

-- Every result must be zero.
*/