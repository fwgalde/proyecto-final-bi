/*
===============================================================================
FILE:
    scripts/04_findings.sql

PURPOSE:
    Produce reproducible numerical findings for the README and final report.

DATABASE:
    Amazon Aurora PostgreSQL
===============================================================================
*/


-- ============================================================================
-- 1. GLOBAL KPIs
-- ============================================================================

SELECT
    COUNT(*) AS observations,
    COUNT(DISTINCT sheep_key) AS sheep_count,
    ROUND(AVG(total_milk_liters), 4) AS avg_milk_liters,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY total_milk_liters)
        AS median_milk_liters,
    MIN(total_milk_liters) AS min_milk_liters,
    MAX(total_milk_liters) AS max_milk_liters,
    ROUND(SUM(total_milk_liters), 2) AS total_milk_liters
FROM sheep_dw.fact_milk_control;


-- ============================================================================
-- 2. PRODUCTION BY LACTATION STAGE
-- ============================================================================

SELECT
    ls.stage_order,
    ls.stage_label,
    COUNT(*) AS observations,
    COUNT(DISTINCT f.sheep_key) AS sheep_count,
    ROUND(AVG(f.total_milk_liters), 4) AS avg_milk_liters,
    ROUND(
        PERCENTILE_CONT(0.5)
            WITHIN GROUP (ORDER BY f.total_milk_liters)::NUMERIC,
        4
    ) AS median_milk_liters,
    ROUND(STDDEV_SAMP(f.total_milk_liters), 4) AS stddev_milk_liters
FROM sheep_dw.fact_milk_control AS f
JOIN sheep_dw.dim_lactation_stage AS ls
  ON ls.lactation_stage_key = f.lactation_stage_key
GROUP BY
    ls.stage_order,
    ls.stage_label
ORDER BY ls.stage_order;


-- ============================================================================
-- 3. MANAGEMENT PERFORMANCE
-- ============================================================================
-- The minimum-observation condition prevents tiny groups from dominating
-- the interpretation.

WITH management_summary AS (
    SELECT
        m.group_space_label,
        m.pen_id,
        COUNT(*) AS observations,
        COUNT(DISTINCT f.sheep_key) AS sheep_count,
        AVG(f.total_milk_liters) AS avg_milk_liters
    FROM sheep_dw.fact_milk_control AS f
    JOIN sheep_dw.dim_management AS m
      ON m.management_key = f.management_key
    GROUP BY
        m.group_space_label,
        m.pen_id
)
SELECT
    group_space_label,
    pen_id,
    observations,
    sheep_count,
    ROUND(avg_milk_liters, 4) AS avg_milk_liters
FROM management_summary
WHERE observations >= 100
ORDER BY avg_milk_liters DESC;


-- ============================================================================
-- 4. DAILY PRODUCTION EXTREMES
-- ============================================================================

WITH daily_summary AS (
    SELECT
        d.full_date AS control_date,
        COUNT(*) AS observations,
        COUNT(DISTINCT f.sheep_key) AS sheep_count,
        AVG(f.total_milk_liters) AS avg_milk_liters
    FROM sheep_dw.fact_milk_control AS f
    JOIN sheep_dw.dim_date AS d
      ON d.date_key = f.control_date_key
    GROUP BY d.full_date
)
(
    SELECT
        'HIGHEST' AS result_type,
        control_date,
        observations,
        sheep_count,
        ROUND(avg_milk_liters, 4) AS avg_milk_liters
    FROM daily_summary
    ORDER BY avg_milk_liters DESC
    LIMIT 5
)

UNION ALL

(
    SELECT
        'LOWEST' AS result_type,
        control_date,
        observations,
        sheep_count,
        ROUND(avg_milk_liters, 4) AS avg_milk_liters
    FROM daily_summary
    ORDER BY avg_milk_liters ASC
    LIMIT 5
);


-- ============================================================================
-- 5. CURRENT-DAY WEATHER CORRELATIONS
-- ============================================================================

SELECT
    ROUND(
        CORR(
            thi::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS corr_thi_milk,

    ROUND(
        CORR(
            avg_temp_c::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS corr_temperature_milk,

    ROUND(
        CORR(
            avg_humidity_pct::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS corr_humidity_milk,

    ROUND(
        CORR(
            precipitation_mm::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS corr_precipitation_milk,

    ROUND(
        CORR(
            radiation_mj_m2::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS corr_radiation_milk

FROM sheep_dw.fact_milk_control;


-- ============================================================================
-- 6. PREVIOUS-DAY WEATHER CORRELATIONS
-- ============================================================================

SELECT
    ROUND(
        CORR(
            thi_previous_day::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS corr_previous_thi_milk,

    ROUND(
        CORR(
            avg_temp_c_previous_day::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS corr_previous_temperature_milk,

    ROUND(
        CORR(
            avg_humidity_pct_previous_day::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS corr_previous_humidity_milk,

    ROUND(
        CORR(
            precipitation_mm_previous_day::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        )::NUMERIC,
        4
    ) AS corr_previous_precipitation_milk

FROM sheep_dw.fact_milk_control;


-- ============================================================================
-- 7. DISTRIBUTION OF OBSERVATIONS PER SHEEP
-- ============================================================================

WITH observations_per_sheep AS (
    SELECT
        sheep_key,
        COUNT(*) AS observation_count
    FROM sheep_dw.fact_milk_control
    GROUP BY sheep_key
)
SELECT
    COUNT(*) AS sheep_count,
    MIN(observation_count) AS min_observations,
    ROUND(AVG(observation_count), 2) AS avg_observations,
    PERCENTILE_CONT(0.5)
        WITHIN GROUP (ORDER BY observation_count)
        AS median_observations,
    MAX(observation_count) AS max_observations,

    COUNT(*) FILTER (
        WHERE observation_count = 1
    ) AS sheep_with_one_observation,

    ROUND(
        COUNT(*) FILTER (
            WHERE observation_count = 1
        )::NUMERIC
        / COUNT(*)
        * 100,
        2
    ) AS pct_sheep_with_one_observation

FROM observations_per_sheep;


-- ============================================================================
-- 8. DATA QUALITY
-- ============================================================================

SELECT
    q.quality_code,
    q.quality_label,
    COUNT(*) AS observations,
    ROUND(
        COUNT(*)::NUMERIC
        / SUM(COUNT(*)) OVER ()
        * 100,
        4
    ) AS percentage
FROM sheep_dw.fact_milk_control AS f
JOIN sheep_dw.dim_data_quality AS q
  ON q.data_quality_key = f.data_quality_key
GROUP BY
    q.quality_code,
    q.quality_label
ORDER BY observations DESC;
