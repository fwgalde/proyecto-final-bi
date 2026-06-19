/*
===============================================================================
PROJECT:
    Data Warehouse for Dairy Sheep Milk Production Analysis

FILE:
    scripts/02_advanced_queries.sql

PURPOSE:
    Demonstrate advanced SQL techniques applied to real analytical questions.

TECHNIQUES:
    1. PL/pgSQL business function
    2. Common Table Expressions (CTEs)
    3. Window functions
    4. GROUPING SETS / OLAP roll-up
    5. Ordered-set aggregates: PERCENTILE_CONT
    6. Statistical functions: STDDEV_SAMP and CORR
    7. NTILE analytical segmentation

DATABASE:
    Amazon Aurora PostgreSQL
===============================================================================
*/


-- ============================================================================
-- 1. BUSINESS FUNCTION: CLASSIFY LACTATION STAGE
-- ============================================================================
-- This function centralizes the same operational business rule used by the ETL.
-- It is useful for:
--   - validation;
--   - ad-hoc analyses;
--   - avoiding duplicated CASE expressions.
--
-- The ranges are project-defined analytical buckets.
-- They are not asserted as universal biological stages.
-- ============================================================================

CREATE OR REPLACE FUNCTION sheep_dw.fn_lactation_stage_key(
    p_days_in_milk INTEGER
)
RETURNS SMALLINT
LANGUAGE plpgsql
IMMUTABLE
STRICT
AS $$
BEGIN
    IF p_days_in_milk < 0 THEN
        RAISE EXCEPTION
            'days_in_milk cannot be negative: %',
            p_days_in_milk;
    ELSIF p_days_in_milk <= 30 THEN
        RETURN 1;
    ELSIF p_days_in_milk <= 60 THEN
        RETURN 2;
    ELSIF p_days_in_milk <= 90 THEN
        RETURN 3;
    ELSIF p_days_in_milk <= 120 THEN
        RETURN 4;
    ELSIF p_days_in_milk <= 180 THEN
        RETURN 5;
    ELSIF p_days_in_milk <= 270 THEN
        RETURN 6;
    ELSIF p_days_in_milk <= 365 THEN
        RETURN 7;
    ELSE
        RETURN 8;
    END IF;
END;
$$;

COMMENT ON FUNCTION sheep_dw.fn_lactation_stage_key(INTEGER) IS
    'Returns the project-defined lactation-stage key for an exact days-in-milk value.';


-- ============================================================================
-- QUERY 1
-- VALIDATE ETL LACTATION-STAGE ASSIGNMENT
-- ============================================================================
-- Advanced technique:
--   PL/pgSQL function used as a business-rule validation.
--
-- Expected result:
--   stage_mismatches = 0
-- ============================================================================

SELECT
    COUNT(*) AS total_observations,

    COUNT(*) FILTER (
        WHERE f.lactation_stage_key
              <> sheep_dw.fn_lactation_stage_key(f.days_in_milk)
    ) AS stage_mismatches

FROM sheep_dw.fact_milk_control AS f;


-- ============================================================================
-- QUERY 2
-- PRODUCTION SUMMARY BY LACTATION STAGE
-- ============================================================================
-- Analytical question:
--   How does milk production vary across operational lactation periods?
--
-- Advanced techniques:
--   - CTE
--   - PERCENTILE_CONT
--   - STDDEV_SAMP
--   - RANK window function
-- ============================================================================

WITH stage_statistics AS (
    SELECT
        ls.lactation_stage_key,
        ls.stage_code,
        ls.stage_label,
        ls.stage_order,

        COUNT(*) AS observation_count,
        COUNT(DISTINCT f.sheep_key) AS sheep_count,

        AVG(f.total_milk_liters) AS avg_milk_liters,

        PERCENTILE_CONT(0.5)
            WITHIN GROUP (
                ORDER BY f.total_milk_liters
            ) AS median_milk_liters,

        STDDEV_SAMP(f.total_milk_liters) AS stddev_milk_liters,

        MIN(f.total_milk_liters) AS min_milk_liters,
        MAX(f.total_milk_liters) AS max_milk_liters

    FROM sheep_dw.fact_milk_control AS f

    JOIN sheep_dw.dim_lactation_stage AS ls
      ON ls.lactation_stage_key = f.lactation_stage_key

    GROUP BY
        ls.lactation_stage_key,
        ls.stage_code,
        ls.stage_label,
        ls.stage_order
),

ranked_stages AS (
    SELECT
        *,

        RANK() OVER (
            ORDER BY avg_milk_liters DESC
        ) AS production_rank

    FROM stage_statistics
)

SELECT
    lactation_stage_key,
    stage_code,
    stage_label,
    stage_order,
    observation_count,
    sheep_count,

    ROUND(avg_milk_liters, 4) AS avg_milk_liters,

    ROUND(
        median_milk_liters::NUMERIC,
        4
    ) AS median_milk_liters,

    ROUND(stddev_milk_liters, 4) AS stddev_milk_liters,
    min_milk_liters,
    max_milk_liters,
    production_rank

FROM ranked_stages

ORDER BY stage_order;


-- ============================================================================
-- QUERY 3
-- LONGITUDINAL PRODUCTION TREND BY SHEEP
-- ============================================================================
-- Analytical question:
--   How does each sheep's production change relative to its previous controls
--   and recent moving average?
--
-- Advanced techniques:
--   - CTE
--   - LAG
--   - moving AVG window
--   - PARTITION BY
--
-- Only sheep with at least five observations are included.
-- LIMIT is used because this is an analytical inspection query.
-- ============================================================================

WITH eligible_sheep AS (
    SELECT
        sheep_key
    FROM sheep_dw.fact_milk_control
    GROUP BY sheep_key
    HAVING COUNT(*) >= 5
),

production_series AS (
    SELECT
        s.animal_code,
        d.full_date AS control_date,
        f.source_row_number,
        f.days_in_milk,
        f.total_milk_liters,

        LAG(f.total_milk_liters) OVER (
            PARTITION BY f.sheep_key
            ORDER BY
                d.full_date,
                f.source_row_number
        ) AS previous_control_milk_liters,

        AVG(f.total_milk_liters) OVER (
            PARTITION BY f.sheep_key
            ORDER BY
                d.full_date,
                f.source_row_number
            ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
        ) AS moving_avg_5_controls

    FROM sheep_dw.fact_milk_control AS f

    JOIN eligible_sheep AS es
      ON es.sheep_key = f.sheep_key

    JOIN sheep_dw.dim_sheep AS s
      ON s.sheep_key = f.sheep_key

    JOIN sheep_dw.dim_date AS d
      ON d.date_key = f.control_date_key
)

SELECT
    animal_code,
    control_date,
    source_row_number,
    days_in_milk,
    total_milk_liters,
    previous_control_milk_liters,

    total_milk_liters
        - previous_control_milk_liters
        AS change_vs_previous_control,

    ROUND(
        moving_avg_5_controls,
        4
    ) AS moving_avg_5_controls

FROM production_series

ORDER BY
    animal_code,
    control_date,
    source_row_number

LIMIT 200;


-- ============================================================================
-- QUERY 4
-- OLAP ROLL-UP: DAY, WEEK, MONTH AND TOTAL
-- ============================================================================
-- Analytical question:
--   How does milk production aggregate when moving from detailed dates
--   toward higher temporal levels?
--
-- Advanced technique:
--   GROUPING SETS
--
-- This implements a true OLAP-style roll-up without creating duplicate
-- physical fact tables.
-- ============================================================================

SELECT
    CASE
        WHEN GROUPING(d.full_date) = 0
            THEN 'DAY'

        WHEN GROUPING(d.week_of_year) = 0
            THEN 'WEEK'

        WHEN GROUPING(d.month) = 0
            THEN 'MONTH'

        ELSE 'TOTAL'
    END AS aggregation_level,

    d.year,
    d.month,
    d.week_of_year,
    d.full_date,

    COUNT(*) AS observation_count,
    COUNT(DISTINCT f.sheep_key) AS sheep_count,

    ROUND(
        AVG(f.total_milk_liters),
        4
    ) AS avg_milk_liters,

    ROUND(
        PERCENTILE_CONT(0.5)
            WITHIN GROUP (
                ORDER BY f.total_milk_liters
            )::NUMERIC,
        4
    ) AS median_milk_liters,

    ROUND(
        SUM(f.total_milk_liters),
        4
    ) AS total_milk_liters

FROM sheep_dw.fact_milk_control AS f

JOIN sheep_dw.dim_date AS d
  ON d.date_key = f.control_date_key

GROUP BY GROUPING SETS (
    (
        d.year,
        d.month,
        d.week_of_year,
        d.full_date
    ),
    (
        d.year,
        d.week_of_year
    ),
    (
        d.year,
        d.month
    ),
    ()
)

ORDER BY
    aggregation_level,
    d.year NULLS LAST,
    d.month NULLS LAST,
    d.week_of_year NULLS LAST,
    d.full_date NULLS LAST;


-- ============================================================================
-- QUERY 5
-- DATA-DRIVEN THI QUARTILES
-- ============================================================================
-- Analytical question:
--   How does milk production vary across quartiles of observed THI?
--
-- This deliberately avoids claiming arbitrary biological heat-stress limits.
-- Quartiles are created from the empirical THI distribution in this dataset.
--
-- Advanced techniques:
--   - CTE
--   - NTILE
--   - PERCENTILE_CONT
--   - STDDEV_SAMP
--   - CORR
-- ============================================================================

WITH thi_ranked AS (
    SELECT
        f.milk_control_key,
        f.thi,
        f.total_milk_liters,

        NTILE(4) OVER (
            ORDER BY f.thi
        ) AS thi_quartile

    FROM sheep_dw.fact_milk_control AS f
),

thi_summary AS (
    SELECT
        thi_quartile,

        COUNT(*) AS observation_count,

        MIN(thi) AS min_thi,
        MAX(thi) AS max_thi,

        AVG(total_milk_liters) AS avg_milk_liters,

        PERCENTILE_CONT(0.5)
            WITHIN GROUP (
                ORDER BY total_milk_liters
            ) AS median_milk_liters,

        STDDEV_SAMP(total_milk_liters) AS stddev_milk_liters,

        CORR(
            thi::DOUBLE PRECISION,
            total_milk_liters::DOUBLE PRECISION
        ) AS thi_milk_correlation

    FROM thi_ranked

    GROUP BY thi_quartile
)

SELECT
    thi_quartile,
    observation_count,
    ROUND(min_thi, 4) AS min_thi,
    ROUND(max_thi, 4) AS max_thi,
    ROUND(avg_milk_liters, 4) AS avg_milk_liters,

    ROUND(
        median_milk_liters::NUMERIC,
        4
    ) AS median_milk_liters,

    ROUND(stddev_milk_liters, 4) AS stddev_milk_liters,

    ROUND(
        thi_milk_correlation::NUMERIC,
        4
    ) AS thi_milk_correlation

FROM thi_summary

ORDER BY thi_quartile;


-- ============================================================================
-- QUERY 6
-- MANAGEMENT / PEN PERFORMANCE RANKING
-- ============================================================================
-- Analytical question:
--   Which pen and group-space combinations show the highest average
--   production?
--
-- Advanced techniques:
--   - CTE
--   - RANK
--   - percentage difference against overall average
-- ============================================================================

WITH overall AS (
    SELECT
        AVG(total_milk_liters) AS overall_avg_milk
    FROM sheep_dw.fact_milk_control
),

management_statistics AS (
    SELECT
        m.management_key,
        m.pen_id,
        m.group_space_code,
        m.group_space_label,

        COUNT(*) AS observation_count,
        COUNT(DISTINCT f.sheep_key) AS sheep_count,

        AVG(f.total_milk_liters) AS avg_milk_liters

    FROM sheep_dw.fact_milk_control AS f

    JOIN sheep_dw.dim_management AS m
      ON m.management_key = f.management_key

    GROUP BY
        m.management_key,
        m.pen_id,
        m.group_space_code,
        m.group_space_label
),

ranked_management AS (
    SELECT
        ms.*,
        o.overall_avg_milk,

        RANK() OVER (
            ORDER BY ms.avg_milk_liters DESC
        ) AS production_rank

    FROM management_statistics AS ms
    CROSS JOIN overall AS o
)

SELECT
    management_key,
    pen_id,
    group_space_code,
    group_space_label,
    observation_count,
    sheep_count,
    ROUND(avg_milk_liters, 4) AS avg_milk_liters,

    ROUND(
        (
            avg_milk_liters
            / NULLIF(overall_avg_milk, 0)
            - 1
        ) * 100,
        2
    ) AS pct_vs_overall_average,

    production_rank

FROM ranked_management

ORDER BY production_rank;


-- ============================================================================
-- QUERY 7
-- DATA-QUALITY DISTRIBUTION
-- ============================================================================
-- Analytical question:
--   What percentage of the warehouse observations is complete?
--
-- Advanced technique:
--   aggregate value divided by window aggregate over grouped results.
-- ============================================================================

WITH quality_counts AS (
    SELECT
        q.quality_code,
        q.quality_label,
        q.has_missing_group_space,
        COUNT(*) AS observation_count

    FROM sheep_dw.fact_milk_control AS f

    JOIN sheep_dw.dim_data_quality AS q
      ON q.data_quality_key = f.data_quality_key

    GROUP BY
        q.quality_code,
        q.quality_label,
        q.has_missing_group_space
)

SELECT
    quality_code,
    quality_label,
    has_missing_group_space,
    observation_count,

    ROUND(
        observation_count::NUMERIC
        / SUM(observation_count) OVER ()
        * 100,
        4
    ) AS percentage_of_total

FROM quality_counts

ORDER BY observation_count DESC;