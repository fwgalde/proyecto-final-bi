from __future__ import annotations

import argparse
import logging
import os
import sys
import time
import unicodedata
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Connection, Engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE_FILE = PROJECT_ROOT / "datasets" / "raw" / "raw_data.xlsx"
LOG_DIR = PROJECT_ROOT / "logs"

MAIN_SHEET = "Hoja1"
CODES_SHEET = "CODIGOS ANIMALES"
WAREHOUSE_SCHEMA = "sheep_dw"

EXPECTED_SOURCE_ROWS = 96_195
EXPECTED_SOURCE_COLUMNS = 57
EXPECTED_SHEEP_COUNT = 13_829
EXPECTED_MISSING_GROUP_SPACE = 18

EXPECTED_DIMENSION_COUNTS = {
    "dim_sheep": 13_829,
    "dim_date": 654,
    "dim_management": 12,
    "dim_weather_condition": 14,
    "dim_lunar": 35,
}

EXPECTED_SOURCE_HEADERS = [
    "Nº de Oveja", "Fecha Parto", "Fecha control", "Ordeño mañana(lts)",
    "Ordeño tarde(lts)", "Dias ordeño ", "Espacio grupo", "Parque(Corral)",
    "Mes de parto", "Dia antes del control", "Fecha Clima", "Temp, media(ºC)",
    "Temp, max(ºC)", "Hora Temp Max", "Temp, min(ºC)", "Hora Temp Min",
    "Hum, med(%)", "Humedad max(%)", "Hora Hum Max", "Humedad min(%)",
    "Hora Hum Min", "THI", "Vel, viento(m/s)", "Dir, viento (º)",
    "Vel, max(m/s)", "Clasificacion velocidad", "Hora Vel Max",
    "Dir, Vel, max (º)", "Radiacion(MJ/m^2)", "Precipitacion(mm)",
    "Clasificacion precipitacion", "Calendario lunar", "Clasif. Cal. lunar",
    "Fecha", "Temp, media(ºC)", "Temp, max(ºC)", "Hora Temp Max",
    "Temp, min(ºC)", "Hora Temp Min", "Hum, med(%)", "Humedad max(%)",
    "Hora Hum Max", "Humedad min(%)", "Hora Hum Min", "ITH Ant",
    "Vel. viento(m/s)", "Dir, viento (º)", "Vel. max(m/s)",
    "Clasificacion Velocidad", "Hora Vel Max", "Vel max (º)", "Radiacion(º)",
    "Precipitacion(mm)", "Clasificacion Precipitacion", "Calendario lunar",
    "Clasf. Cal. lunar", "Leche Total",
]

CANONICAL_COLUMNS = [
    "sheep_id", "lambing_date", "control_date", "morning_milking_liters",
    "afternoon_milking_liters", "days_in_milk", "group_space", "pen_id",
    "lambing_month_source", "date_before_control_source", "weather_date_source",
    "avg_temp_c", "max_temp_c", "max_temp_time_source", "min_temp_c",
    "min_temp_time_source", "avg_humidity_pct", "max_humidity_pct",
    "max_humidity_time_source", "min_humidity_pct", "min_humidity_time_source",
    "thi", "wind_speed_mps", "wind_direction_deg", "max_wind_speed_mps",
    "wind_speed_category", "max_wind_time_source", "max_wind_direction_deg",
    "radiation_mj_m2", "precipitation_mm", "precipitation_category",
    "lunar_phase", "lunar_phase_index", "previous_weather_date_source",
    "avg_temp_c_previous_day", "max_temp_c_previous_day",
    "max_temp_time_previous_day_source", "min_temp_c_previous_day",
    "min_temp_time_previous_day_source", "avg_humidity_pct_previous_day",
    "max_humidity_pct_previous_day", "max_humidity_time_previous_day_source",
    "min_humidity_pct_previous_day", "min_humidity_time_previous_day_source",
    "thi_previous_day", "wind_speed_mps_previous_day",
    "wind_direction_deg_previous_day", "max_wind_speed_mps_previous_day",
    "wind_speed_category_previous_day", "max_wind_time_previous_day_source",
    "max_wind_direction_deg_previous_day", "radiation_mj_m2_previous_day",
    "precipitation_mm_previous_day", "precipitation_category_previous_day",
    "lunar_phase_previous_day", "lunar_phase_index_previous_day",
    "total_milk_liters",
]

DATE_COLUMNS = [
    "lambing_date",
    "control_date",
    "date_before_control_source",
    "weather_date_source",
    "previous_weather_date_source",
]

INTEGER_COLUMNS = [
    "sheep_id",
    "days_in_milk",
    "group_space",
    "pen_id",
    "lambing_month_source",
    "wind_speed_category",
    "precipitation_category",
    "lunar_phase_index",
    "wind_speed_category_previous_day",
    "precipitation_category_previous_day",
    "lunar_phase_index_previous_day",
]

FLOAT_COLUMNS = [
    "morning_milking_liters",
    "afternoon_milking_liters",
    "total_milk_liters",
    "avg_temp_c",
    "max_temp_c",
    "min_temp_c",
    "avg_humidity_pct",
    "max_humidity_pct",
    "min_humidity_pct",
    "thi",
    "wind_speed_mps",
    "wind_direction_deg",
    "max_wind_speed_mps",
    "max_wind_direction_deg",
    "radiation_mj_m2",
    "precipitation_mm",
    "avg_temp_c_previous_day",
    "max_temp_c_previous_day",
    "min_temp_c_previous_day",
    "avg_humidity_pct_previous_day",
    "max_humidity_pct_previous_day",
    "min_humidity_pct_previous_day",
    "thi_previous_day",
    "wind_speed_mps_previous_day",
    "wind_direction_deg_previous_day",
    "max_wind_speed_mps_previous_day",
    "max_wind_direction_deg_previous_day",
    "radiation_mj_m2_previous_day",
    "precipitation_mm_previous_day",
]

FACT_MEASURE_COLUMNS = [
    "morning_milking_liters",
    "afternoon_milking_liters",
    "total_milk_liters",
    "days_in_milk",
    "avg_temp_c",
    "max_temp_c",
    "min_temp_c",
    "avg_humidity_pct",
    "max_humidity_pct",
    "min_humidity_pct",
    "thi",
    "wind_speed_mps",
    "wind_direction_deg",
    "max_wind_speed_mps",
    "max_wind_direction_deg",
    "radiation_mj_m2",
    "precipitation_mm",
    "avg_temp_c_previous_day",
    "max_temp_c_previous_day",
    "min_temp_c_previous_day",
    "avg_humidity_pct_previous_day",
    "max_humidity_pct_previous_day",
    "min_humidity_pct_previous_day",
    "thi_previous_day",
    "wind_speed_mps_previous_day",
    "wind_direction_deg_previous_day",
    "max_wind_speed_mps_previous_day",
    "max_wind_direction_deg_previous_day",
    "radiation_mj_m2_previous_day",
    "precipitation_mm_previous_day",
]

MONTH_NAMES = {
    1: "January", 2: "February", 3: "March", 4: "April",
    5: "May", 6: "June", 7: "July", 8: "August",
    9: "September", 10: "October", 11: "November", 12: "December",
}

DAY_NAMES = {
    1: "Monday", 2: "Tuesday", 3: "Wednesday", 4: "Thursday",
    5: "Friday", 6: "Saturday", 7: "Sunday",
}


class ETLValidationError(RuntimeError):
    """Raised when source or post-load validation fails."""


def configure_logging() -> logging.Logger:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"etl_{pd.Timestamp.now():%Y%m%d_%H%M%S}.log"

    logger = logging.getLogger("sheep_etl")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.info("Log file: %s", log_path)
    return logger


def normalize_header(value: Any) -> str:
    if pd.isna(value):
        return ""
    return unicodedata.normalize("NFKC", str(value)).strip()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ETLValidationError(message)


def get_source_path() -> Path:
    configured = os.getenv("SOURCE_FILE", "").strip()
    path = Path(configured).expanduser() if configured else DEFAULT_SOURCE_FILE
    if not path.is_absolute():
        path = (PROJECT_ROOT / path).resolve()
    require(path.exists(), f"Source workbook not found: {path}")
    return path


def get_engine() -> Engine:
    required_names = ["DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    missing = [name for name in required_names if not os.getenv(name)]
    require(not missing, f"Missing database variables in .env: {', '.join(missing)}")

    url = URL.create(
        drivername="postgresql+psycopg2",
        username=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        database=os.environ["DB_NAME"],
    )

    connect_args: dict[str, Any] = {
        "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "20")),
    }
    sslmode = os.getenv("DB_SSLMODE", "").strip()
    if sslmode:
        connect_args["sslmode"] = sslmode

    return create_engine(
        url,
        pool_pre_ping=True,
        connect_args=connect_args,
        future=True,
    )


def extract_source(source_path: Path, logger: logging.Logger) -> tuple[pd.DataFrame, pd.DataFrame]:
    logger.info("EXTRACT | Reading workbook: %s", source_path)
    started = time.perf_counter()

    with pd.ExcelFile(source_path, engine="openpyxl") as workbook:
        required_sheets = {MAIN_SHEET, CODES_SHEET}
        missing_sheets = required_sheets.difference(workbook.sheet_names)
        require(not missing_sheets, f"Missing required sheets: {sorted(missing_sheets)}")

        # header=None intentionally preserves duplicate Excel headers by position.
        raw_with_header = pd.read_excel(
            workbook,
            sheet_name=MAIN_SHEET,
            header=None,
        )
        codes = pd.read_excel(
            workbook,
            sheet_name=CODES_SHEET,
            usecols=["Nº de Oveja", "O"],
        )

    require(len(raw_with_header) >= 2, f"Sheet {MAIN_SHEET} has no data rows")
    require(
        raw_with_header.shape[1] == EXPECTED_SOURCE_COLUMNS,
        f"Expected {EXPECTED_SOURCE_COLUMNS} columns in {MAIN_SHEET}, found {raw_with_header.shape[1]}",
    )

    actual_headers = [normalize_header(v) for v in raw_with_header.iloc[0].tolist()]
    expected_headers = [normalize_header(v) for v in EXPECTED_SOURCE_HEADERS]
    if actual_headers != expected_headers:
        mismatches = [
            f"position {i + 1}: expected={expected!r}, actual={actual!r}"
            for i, (expected, actual) in enumerate(zip(expected_headers, actual_headers))
            if expected != actual
        ]
        raise ETLValidationError(
            "The header contract changed. First mismatches: " + "; ".join(mismatches[:10])
        )

    raw = raw_with_header.iloc[1:].reset_index(drop=True).copy()
    raw.columns = CANONICAL_COLUMNS
    raw.insert(0, "source_row_number", np.arange(2, len(raw) + 2, dtype=np.int64))

    codes = codes.rename(columns={"Nº de Oveja": "sheep_id", "O": "animal_code"})

    logger.info(
        "EXTRACT | Hoja1 rows=%s columns=%s | CODIGOS ANIMALES rows=%s | %.2fs",
        f"{len(raw):,}",
        len(CANONICAL_COLUMNS),
        f"{len(codes):,}",
        time.perf_counter() - started,
    )
    return raw, codes


def coerce_numeric(series: pd.Series, column_name: str) -> pd.Series:
    original_not_null = series.notna()
    if pd.api.types.is_numeric_dtype(series):
        converted = pd.to_numeric(series, errors="coerce")
    else:
        cleaned = (
            series.astype("string")
            .str.strip()
            .str.replace(",", ".", regex=False)
        )
        converted = pd.to_numeric(cleaned, errors="coerce")

    invalid = original_not_null & converted.isna()
    if invalid.any():
        examples = series.loc[invalid].astype(str).head(5).tolist()
        raise ETLValidationError(
            f"Column {column_name!r} contains non-numeric values. Examples: {examples}"
        )
    return converted


def coerce_integer(series: pd.Series, column_name: str, allow_null: bool = False) -> pd.Series:
    numeric = coerce_numeric(series, column_name)
    if not allow_null and numeric.isna().any():
        raise ETLValidationError(f"Column {column_name!r} contains null values")

    non_null = numeric.dropna().to_numpy(dtype=float)
    if len(non_null) and not np.all(np.isclose(non_null, np.round(non_null), atol=1e-9)):
        examples = numeric.loc[~np.isclose(numeric.fillna(0), np.round(numeric.fillna(0)), atol=1e-9)].head(5)
        raise ETLValidationError(
            f"Column {column_name!r} contains non-integer values: {examples.tolist()}"
        )
    return numeric.round().astype("Int64")


def coerce_date(series: pd.Series, column_name: str) -> pd.Series:
    original_not_null = series.notna()
    converted = pd.to_datetime(series, errors="coerce").dt.normalize()
    invalid = original_not_null & converted.isna()
    if invalid.any():
        examples = series.loc[invalid].astype(str).head(5).tolist()
        raise ETLValidationError(
            f"Column {column_name!r} contains invalid dates. Examples: {examples}"
        )
    require(not converted.isna().any(), f"Column {column_name!r} contains null dates")
    return converted


def transform_source(
    raw: pd.DataFrame,
    codes: pd.DataFrame,
    logger: logging.Logger,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    logger.info("TRANSFORM | Cleaning and typing source data")
    started = time.perf_counter()

    df = raw.copy()
    code_df = codes.copy()

    require(len(df) == EXPECTED_SOURCE_ROWS, f"Expected {EXPECTED_SOURCE_ROWS:,} source rows, found {len(df):,}")
    require(df["source_row_number"].is_unique, "source_row_number is not unique")

    for column in DATE_COLUMNS:
        df[column] = coerce_date(df[column], column)

    for column in FLOAT_COLUMNS:
        df[column] = coerce_numeric(df[column], column).astype(float)

    for column in INTEGER_COLUMNS:
        df[column] = coerce_integer(
            df[column],
            column,
            allow_null=(column == "group_space"),
        )

    df["lunar_phase"] = df["lunar_phase"].astype("string").str.strip().str.lower()
    df["lunar_phase_previous_day"] = (
        df["lunar_phase_previous_day"].astype("string").str.strip().str.lower()
    )
    require(not df["lunar_phase"].isna().any(), "lunar_phase contains nulls")
    require(not df["lunar_phase_previous_day"].isna().any(), "lunar_phase_previous_day contains nulls")

    df["has_missing_group_space"] = df["group_space"].isna()
    missing_group_space = int(df["has_missing_group_space"].sum())
    require(
        missing_group_space == EXPECTED_MISSING_GROUP_SPACE,
        f"Expected {EXPECTED_MISSING_GROUP_SPACE} missing group-space rows, found {missing_group_space}",
    )
    df["group_space"] = df["group_space"].fillna(-1).astype("int64")

    for column in [c for c in INTEGER_COLUMNS if c != "group_space"]:
        df[column] = df[column].astype("int64")

    code_df["sheep_id"] = coerce_integer(code_df["sheep_id"], "CODIGOS ANIMALES.sheep_id").astype("int64")
    code_df["animal_code"] = code_df["animal_code"].astype("string").str.strip()
    require(not code_df["animal_code"].isna().any(), "CODIGOS ANIMALES contains null animal codes")
    require((code_df["animal_code"] != "").all(), "CODIGOS ANIMALES contains empty animal codes")
    require(code_df["sheep_id"].is_unique, "CODIGOS ANIMALES contains duplicate sheep_id values")
    require(code_df["animal_code"].is_unique, "CODIGOS ANIMALES contains duplicate animal_code values")

    validate_source(df, code_df, logger)

    logger.info("TRANSFORM | Completed in %.2fs", time.perf_counter() - started)
    return df, code_df


def validate_range(df: pd.DataFrame, column: str, minimum: float | None, maximum: float | None) -> None:
    if minimum is not None:
        require((df[column] >= minimum).all(), f"{column} contains values below {minimum}")
    if maximum is not None:
        require((df[column] <= maximum).all(), f"{column} contains values above {maximum}")


def validate_source(df: pd.DataFrame, codes: pd.DataFrame, logger: logging.Logger) -> None:
    logger.info("VALIDATE SOURCE | Running business-rule checks")

    require(df.shape[0] == EXPECTED_SOURCE_ROWS, "Unexpected source row count")
    require(df["sheep_id"].nunique() == EXPECTED_SHEEP_COUNT, "Unexpected distinct sheep count")

    duplicate_rows = int(df.drop(columns=["source_row_number"]).duplicated().sum())
    require(duplicate_rows == 0, f"Found {duplicate_rows} exact duplicate source rows")

    source_sheep = set(df["sheep_id"].unique())
    code_sheep = set(codes["sheep_id"].unique())
    missing_codes = sorted(source_sheep.difference(code_sheep))
    require(not missing_codes, f"Sheep without animal code. First IDs: {missing_codes[:10]}")

    milk_balance = np.isclose(
        df["total_milk_liters"],
        df["morning_milking_liters"] + df["afternoon_milking_liters"],
        atol=0.01,
        rtol=0,
    )
    require(bool(milk_balance.all()), f"Milk balance failed in {(~milk_balance).sum()} rows")

    calculated_days = (df["control_date"] - df["lambing_date"]).dt.days
    require(
        bool((calculated_days == df["days_in_milk"]).all()),
        f"days_in_milk rule failed in {(calculated_days != df['days_in_milk']).sum()} rows",
    )

    require(
        bool((df["lambing_month_source"] == df["lambing_date"].dt.month).all()),
        "lambing_month_source does not match lambing_date",
    )
    require(
        bool((df["weather_date_source"] == df["control_date"]).all()),
        "weather_date_source does not match control_date",
    )

    expected_previous_date = df["control_date"] - pd.Timedelta(days=1)
    require(
        bool((df["date_before_control_source"] == expected_previous_date).all()),
        "date_before_control_source is not control_date - 1 day",
    )
    require(
        bool((df["previous_weather_date_source"] == expected_previous_date).all()),
        "previous_weather_date_source is not control_date - 1 day",
    )

    required_non_null = [
        "sheep_id", "lambing_date", "control_date", "pen_id",
        "wind_speed_category", "precipitation_category", "lunar_phase",
        "lunar_phase_index", "wind_speed_category_previous_day",
        "precipitation_category_previous_day", "lunar_phase_previous_day",
        "lunar_phase_index_previous_day",
        *FACT_MEASURE_COLUMNS,
    ]
    null_counts = df[required_non_null].isna().sum()
    bad_nulls = null_counts[null_counts > 0]
    require(bad_nulls.empty, f"Unexpected nulls in required columns: {bad_nulls.to_dict()}")

    for column in ["morning_milking_liters", "afternoon_milking_liters", "total_milk_liters", "days_in_milk"]:
        validate_range(df, column, 0, None)

    for column in [
        "avg_humidity_pct", "max_humidity_pct", "min_humidity_pct",
        "avg_humidity_pct_previous_day", "max_humidity_pct_previous_day",
        "min_humidity_pct_previous_day",
    ]:
        validate_range(df, column, 0, 100)

    for column in [
        "wind_speed_mps", "max_wind_speed_mps", "radiation_mj_m2", "precipitation_mm",
        "wind_speed_mps_previous_day", "max_wind_speed_mps_previous_day",
        "radiation_mj_m2_previous_day", "precipitation_mm_previous_day",
    ]:
        validate_range(df, column, 0, None)

    for column in [
        "wind_direction_deg", "max_wind_direction_deg",
        "wind_direction_deg_previous_day", "max_wind_direction_deg_previous_day",
    ]:
        validate_range(df, column, 0, 360)

    logger.info(
        "VALIDATE SOURCE | PASS | rows=%s sheep=%s controls=%s..%s milk_avg=%.4f missing_group_space=%s",
        f"{len(df):,}",
        f"{df['sheep_id'].nunique():,}",
        df["control_date"].min().date(),
        df["control_date"].max().date(),
        df["total_milk_liters"].mean(),
        int(df["has_missing_group_space"].sum()),
    )


def date_key(series: pd.Series) -> pd.Series:
    return (
        series.dt.year * 10_000
        + series.dt.month * 100
        + series.dt.day
    ).astype("int64")


def management_natural_key(group_space: pd.Series, pen_id: pd.Series) -> pd.Series:
    return "space=" + group_space.astype(str) + "|pen=" + pen_id.astype(str)


def weather_natural_key(wind_category: pd.Series, precipitation_category: pd.Series) -> pd.Series:
    return "wind=" + wind_category.astype(str) + "|precipitation=" + precipitation_category.astype(str)


def lunar_natural_key(phase: pd.Series, index: pd.Series) -> pd.Series:
    return "phase=" + phase.astype(str) + "|index=" + index.astype(str)


def build_dimensions(
    df: pd.DataFrame,
    codes: pd.DataFrame,
    logger: logging.Logger,
) -> dict[str, pd.DataFrame]:
    logger.info("BUILD | Creating dynamic dimensions")

    source_sheep = pd.DataFrame({"sheep_id": sorted(df["sheep_id"].unique())})
    dim_sheep = source_sheep.merge(
        codes[["sheep_id", "animal_code"]],
        on="sheep_id",
        how="left",
        validate="one_to_one",
    )
    require(not dim_sheep["animal_code"].isna().any(), "dim_sheep contains missing animal codes")

    min_date = min(df["lambing_date"].min(), df["control_date"].min())
    max_date = max(df["lambing_date"].max(), df["control_date"].max())
    calendar = pd.date_range(min_date, max_date, freq="D")
    dim_date = pd.DataFrame({"full_date": calendar})
    dim_date["date_key"] = date_key(dim_date["full_date"])
    dim_date["year"] = dim_date["full_date"].dt.year.astype("int16")
    dim_date["quarter"] = dim_date["full_date"].dt.quarter.astype("int16")
    dim_date["month"] = dim_date["full_date"].dt.month.astype("int16")
    dim_date["month_name"] = dim_date["month"].map(MONTH_NAMES)
    iso = dim_date["full_date"].dt.isocalendar()
    dim_date["week_of_year"] = iso.week.astype("int16")
    dim_date["day_of_month"] = dim_date["full_date"].dt.day.astype("int16")
    dim_date["day_of_year"] = dim_date["full_date"].dt.dayofyear.astype("int16")
    dim_date["day_of_week"] = dim_date["full_date"].dt.isocalendar().day.astype("int16")
    dim_date["day_name"] = dim_date["day_of_week"].map(DAY_NAMES)
    dim_date["is_weekend"] = dim_date["day_of_week"].isin([6, 7])
    dim_date["full_date"] = dim_date["full_date"].dt.date
    dim_date = dim_date[
        [
            "date_key", "full_date", "year", "quarter", "month", "month_name",
            "week_of_year", "day_of_month", "day_of_year", "day_of_week",
            "day_name", "is_weekend",
        ]
    ]

    dim_management = (
        df[["group_space", "pen_id"]]
        .drop_duplicates()
        .sort_values(["group_space", "pen_id"])
        .reset_index(drop=True)
        .rename(columns={"group_space": "group_space_code"})
    )
    dim_management["group_space_label"] = np.where(
        dim_management["group_space_code"] == -1,
        "Unknown",
        "Group space " + dim_management["group_space_code"].astype(str),
    )
    dim_management["management_natural_key"] = management_natural_key(
        dim_management["group_space_code"], dim_management["pen_id"]
    )
    dim_management = dim_management[
        ["group_space_code", "group_space_label", "pen_id", "management_natural_key"]
    ]

    current_weather = df[["wind_speed_category", "precipitation_category"]].copy()
    previous_weather = df[
        ["wind_speed_category_previous_day", "precipitation_category_previous_day"]
    ].rename(
        columns={
            "wind_speed_category_previous_day": "wind_speed_category",
            "precipitation_category_previous_day": "precipitation_category",
        }
    )
    dim_weather = (
        pd.concat([current_weather, previous_weather], ignore_index=True)
        .drop_duplicates()
        .sort_values(["wind_speed_category", "precipitation_category"])
        .reset_index(drop=True)
    )
    dim_weather["weather_natural_key"] = weather_natural_key(
        dim_weather["wind_speed_category"], dim_weather["precipitation_category"]
    )

    current_lunar = df[["lunar_phase", "lunar_phase_index"]].copy()
    previous_lunar = df[["lunar_phase_previous_day", "lunar_phase_index_previous_day"]].rename(
        columns={
            "lunar_phase_previous_day": "lunar_phase",
            "lunar_phase_index_previous_day": "lunar_phase_index",
        }
    )
    dim_lunar = (
        pd.concat([current_lunar, previous_lunar], ignore_index=True)
        .drop_duplicates()
        .sort_values(["lunar_phase", "lunar_phase_index"])
        .reset_index(drop=True)
    )
    dim_lunar["lunar_natural_key"] = lunar_natural_key(
        dim_lunar["lunar_phase"], dim_lunar["lunar_phase_index"]
    )

    dimensions = {
        "dim_sheep": dim_sheep[["sheep_id", "animal_code"]],
        "dim_date": dim_date,
        "dim_management": dim_management,
        "dim_weather_condition": dim_weather,
        "dim_lunar": dim_lunar,
    }

    for table_name, expected_count in EXPECTED_DIMENSION_COUNTS.items():
        actual = len(dimensions[table_name])
        require(
            actual == expected_count,
            f"{table_name}: expected {expected_count:,} rows, built {actual:,}",
        )
        logger.info("BUILD | %s rows=%s", table_name, f"{actual:,}")

    return dimensions


def ensure_warehouse_exists(connection: Connection) -> None:
    exists = connection.execute(
        text("SELECT to_regclass('sheep_dw.fact_milk_control') IS NOT NULL")
    ).scalar_one()
    require(bool(exists), "sheep_dw.fact_milk_control does not exist. Run 01_schema_ddl.sql first.")


def validate_static_catalogs(connection: Connection) -> None:
    stage_count = connection.execute(
        text("SELECT COUNT(*) FROM sheep_dw.dim_lactation_stage")
    ).scalar_one()
    quality_count = connection.execute(
        text("SELECT COUNT(*) FROM sheep_dw.dim_data_quality")
    ).scalar_one()
    require(stage_count == 8, f"Expected 8 lactation stages, found {stage_count}")
    require(quality_count == 2, f"Expected 2 data-quality rows, found {quality_count}")


def truncate_dynamic_tables(connection: Connection, logger: logging.Logger) -> None:
    logger.info("LOAD | Truncating dynamic warehouse tables")
    connection.execute(
        text(
            """
            TRUNCATE TABLE
                sheep_dw.fact_milk_control,
                sheep_dw.dim_sheep,
                sheep_dw.dim_date,
                sheep_dw.dim_management,
                sheep_dw.dim_weather_condition,
                sheep_dw.dim_lunar
            RESTART IDENTITY;
            """
        )
    )


def load_dataframe(
    connection: Connection,
    dataframe: pd.DataFrame,
    table_name: str,
    chunk_size: int,
    logger: logging.Logger,
) -> None:
    logger.info("LOAD | %s rows=%s", table_name, f"{len(dataframe):,}")
    dataframe.to_sql(
        name=table_name,
        con=connection,
        schema=WAREHOUSE_SCHEMA,
        if_exists="append",
        index=False,
        chunksize=chunk_size,
        method="multi",
    )


def query_dataframe(connection: Connection, sql: str) -> pd.DataFrame:
    return pd.read_sql_query(text(sql), connection)


def map_or_fail(series: pd.Series, mapping: dict[Any, Any], label: str) -> pd.Series:
    result = series.map(mapping)
    if result.isna().any():
        examples = series.loc[result.isna()].drop_duplicates().head(10).tolist()
        raise ETLValidationError(f"Could not resolve {label}. Examples: {examples}")
    return result.astype("int64")


def derive_lactation_stage_keys(days_in_milk: pd.Series, stages: pd.DataFrame) -> pd.Series:
    result = pd.Series(pd.NA, index=days_in_milk.index, dtype="Int64")
    for row in stages.itertuples(index=False):
        mask = days_in_milk >= int(row.min_days_in_milk)
        if pd.notna(row.max_days_in_milk):
            mask &= days_in_milk <= int(row.max_days_in_milk)
        result.loc[mask] = int(row.lactation_stage_key)
    require(not result.isna().any(), "Some days_in_milk values did not match a lactation stage")
    return result.astype("int64")


def build_fact(
    df: pd.DataFrame,
    connection: Connection,
    logger: logging.Logger,
) -> pd.DataFrame:
    logger.info("BUILD | Resolving surrogate keys for fact_milk_control")

    db_sheep = query_dataframe(
        connection,
        "SELECT sheep_key, sheep_id FROM sheep_dw.dim_sheep",
    )
    db_management = query_dataframe(
        connection,
        "SELECT management_key, management_natural_key FROM sheep_dw.dim_management",
    )
    db_weather = query_dataframe(
        connection,
        "SELECT weather_condition_key, weather_natural_key FROM sheep_dw.dim_weather_condition",
    )
    db_lunar = query_dataframe(
        connection,
        "SELECT lunar_key, lunar_natural_key FROM sheep_dw.dim_lunar",
    )
    stages = query_dataframe(
        connection,
        """
        SELECT lactation_stage_key, min_days_in_milk, max_days_in_milk
        FROM sheep_dw.dim_lactation_stage
        ORDER BY stage_order
        """,
    )
    db_quality = query_dataframe(
        connection,
        "SELECT data_quality_key, quality_code FROM sheep_dw.dim_data_quality",
    )

    sheep_map = dict(zip(db_sheep["sheep_id"], db_sheep["sheep_key"]))
    management_map = dict(zip(db_management["management_natural_key"], db_management["management_key"]))
    weather_map = dict(zip(db_weather["weather_natural_key"], db_weather["weather_condition_key"]))
    lunar_map = dict(zip(db_lunar["lunar_natural_key"], db_lunar["lunar_key"]))
    quality_map = dict(zip(db_quality["quality_code"], db_quality["data_quality_key"]))

    fact = pd.DataFrame(index=df.index)
    fact["source_row_number"] = df["source_row_number"].astype("int64")
    fact["sheep_key"] = map_or_fail(df["sheep_id"], sheep_map, "sheep_key")
    fact["control_date_key"] = date_key(df["control_date"])
    fact["lambing_date_key"] = date_key(df["lambing_date"])
    fact["lactation_stage_key"] = derive_lactation_stage_keys(df["days_in_milk"], stages)

    management_keys = management_natural_key(df["group_space"], df["pen_id"])
    fact["management_key"] = map_or_fail(management_keys, management_map, "management_key")

    current_weather_keys = weather_natural_key(
        df["wind_speed_category"], df["precipitation_category"]
    )
    previous_weather_keys = weather_natural_key(
        df["wind_speed_category_previous_day"],
        df["precipitation_category_previous_day"],
    )
    fact["current_weather_condition_key"] = map_or_fail(
        current_weather_keys, weather_map, "current_weather_condition_key"
    )
    fact["previous_weather_condition_key"] = map_or_fail(
        previous_weather_keys, weather_map, "previous_weather_condition_key"
    )

    current_lunar_keys = lunar_natural_key(df["lunar_phase"], df["lunar_phase_index"])
    previous_lunar_keys = lunar_natural_key(
        df["lunar_phase_previous_day"], df["lunar_phase_index_previous_day"]
    )
    fact["current_lunar_key"] = map_or_fail(
        current_lunar_keys, lunar_map, "current_lunar_key"
    )
    fact["previous_lunar_key"] = map_or_fail(
        previous_lunar_keys, lunar_map, "previous_lunar_key"
    )

    quality_codes = pd.Series(
        np.where(df["has_missing_group_space"], "MISSING_GROUP_SPACE", "COMPLETE"),
        index=df.index,
    )
    fact["data_quality_key"] = map_or_fail(quality_codes, quality_map, "data_quality_key")

    for column in FACT_MEASURE_COLUMNS:
        fact[column] = df[column]

    expected_fact_columns = [
        "source_row_number",
        "sheep_key",
        "control_date_key",
        "lambing_date_key",
        "lactation_stage_key",
        "management_key",
        "current_weather_condition_key",
        "previous_weather_condition_key",
        "current_lunar_key",
        "previous_lunar_key",
        "data_quality_key",
        *FACT_MEASURE_COLUMNS,
    ]
    fact = fact[expected_fact_columns]

    require(len(fact) == EXPECTED_SOURCE_ROWS, "Fact row count changed during key resolution")
    null_counts = fact.isna().sum()
    bad_nulls = null_counts[null_counts > 0]
    require(bad_nulls.empty, f"Fact contains nulls: {bad_nulls.to_dict()}")
    require(fact["source_row_number"].is_unique, "Fact source_row_number is not unique")

    logger.info("BUILD | fact_milk_control rows=%s columns=%s", f"{len(fact):,}", len(fact.columns))
    return fact


def scalar(connection: Connection, sql: str) -> Any:
    return connection.execute(text(sql)).scalar_one()


def validate_post_load(
    connection: Connection,
    expected_dimensions: dict[str, pd.DataFrame],
    logger: logging.Logger,
) -> None:
    logger.info("VALIDATE LOAD | Running database checks")

    for table_name, dataframe in expected_dimensions.items():
        actual = scalar(connection, f"SELECT COUNT(*) FROM sheep_dw.{table_name}")
        require(actual == len(dataframe), f"{table_name}: expected {len(dataframe)}, loaded {actual}")

    fact_count = scalar(connection, "SELECT COUNT(*) FROM sheep_dw.fact_milk_control")
    distinct_source_rows = scalar(
        connection,
        "SELECT COUNT(DISTINCT source_row_number) FROM sheep_dw.fact_milk_control",
    )
    require(fact_count == EXPECTED_SOURCE_ROWS, f"Expected {EXPECTED_SOURCE_ROWS} fact rows, loaded {fact_count}")
    require(distinct_source_rows == EXPECTED_SOURCE_ROWS, "Duplicate source_row_number values after load")

    min_source_row = scalar(connection, "SELECT MIN(source_row_number) FROM sheep_dw.fact_milk_control")
    max_source_row = scalar(connection, "SELECT MAX(source_row_number) FROM sheep_dw.fact_milk_control")
    require(min_source_row == 2, f"Expected minimum source row 2, found {min_source_row}")
    require(max_source_row == EXPECTED_SOURCE_ROWS + 1, f"Unexpected maximum source row: {max_source_row}")

    missing_group_count = scalar(
        connection,
        """
        SELECT COUNT(*)
        FROM sheep_dw.fact_milk_control f
        JOIN sheep_dw.dim_data_quality q
          ON q.data_quality_key = f.data_quality_key
        WHERE q.quality_code = 'MISSING_GROUP_SPACE'
        """,
    )
    require(
        missing_group_count == EXPECTED_MISSING_GROUP_SPACE,
        f"Expected {EXPECTED_MISSING_GROUP_SPACE} missing-group-space facts, found {missing_group_count}",
    )

    bad_milk_balance = scalar(
        connection,
        """
        SELECT COUNT(*)
        FROM sheep_dw.fact_milk_control
        WHERE ABS(total_milk_liters - morning_milking_liters - afternoon_milking_liters) > 0.01
        """,
    )
    require(bad_milk_balance == 0, f"Database contains {bad_milk_balance} milk-balance failures")

    orphan_count = scalar(
        connection,
        """
        SELECT COUNT(*)
        FROM sheep_dw.fact_milk_control f
        LEFT JOIN sheep_dw.dim_sheep s
          ON s.sheep_key = f.sheep_key
        LEFT JOIN sheep_dw.dim_date dc
          ON dc.date_key = f.control_date_key
        LEFT JOIN sheep_dw.dim_date dl
          ON dl.date_key = f.lambing_date_key
        LEFT JOIN sheep_dw.dim_lactation_stage ls
          ON ls.lactation_stage_key = f.lactation_stage_key
        LEFT JOIN sheep_dw.dim_management m
          ON m.management_key = f.management_key
        LEFT JOIN sheep_dw.dim_weather_condition wc
          ON wc.weather_condition_key = f.current_weather_condition_key
        LEFT JOIN sheep_dw.dim_weather_condition wp
          ON wp.weather_condition_key = f.previous_weather_condition_key
        LEFT JOIN sheep_dw.dim_lunar lc
          ON lc.lunar_key = f.current_lunar_key
        LEFT JOIN sheep_dw.dim_lunar lp
          ON lp.lunar_key = f.previous_lunar_key
        LEFT JOIN sheep_dw.dim_data_quality q
          ON q.data_quality_key = f.data_quality_key
        WHERE s.sheep_key IS NULL
           OR dc.date_key IS NULL
           OR dl.date_key IS NULL
           OR ls.lactation_stage_key IS NULL
           OR m.management_key IS NULL
           OR wc.weather_condition_key IS NULL
           OR wp.weather_condition_key IS NULL
           OR lc.lunar_key IS NULL
           OR lp.lunar_key IS NULL
           OR q.data_quality_key IS NULL
        """,
    )
    require(orphan_count == 0, f"Found {orphan_count} facts with orphaned foreign keys")

    logger.info(
        "VALIDATE LOAD | PASS | fact=%s sheep=%s dates=%s management=%s weather=%s lunar=%s",
        f"{fact_count:,}",
        f"{len(expected_dimensions['dim_sheep']):,}",
        f"{len(expected_dimensions['dim_date']):,}",
        f"{len(expected_dimensions['dim_management']):,}",
        f"{len(expected_dimensions['dim_weather_condition']):,}",
        f"{len(expected_dimensions['dim_lunar']):,}",
    )


def run_etl(validate_only: bool = False) -> None:
    load_dotenv(PROJECT_ROOT / ".env")
    logger = configure_logging()
    source_path = get_source_path()

    try:
        raw, codes = extract_source(source_path, logger)
        clean_df, clean_codes = transform_source(raw, codes, logger)
        dimensions = build_dimensions(clean_df, clean_codes, logger)

        if validate_only:
            logger.info("VALIDATE-ONLY | PASS | Database was not modified")
            return

        chunk_size = int(os.getenv("ETL_CHUNK_SIZE", "500"))
        require(chunk_size > 0, "ETL_CHUNK_SIZE must be greater than zero")
        engine = get_engine()

        logger.info("LOAD | Opening database transaction")
        with engine.begin() as connection:
            ensure_warehouse_exists(connection)
            validate_static_catalogs(connection)
            truncate_dynamic_tables(connection, logger)

            for table_name in [
                "dim_sheep",
                "dim_date",
                "dim_management",
                "dim_weather_condition",
                "dim_lunar",
            ]:
                load_dataframe(
                    connection,
                    dimensions[table_name],
                    table_name,
                    chunk_size,
                    logger,
                )

            fact = build_fact(clean_df, connection, logger)
            load_dataframe(
                connection,
                fact,
                "fact_milk_control",
                chunk_size,
                logger,
            )
            validate_post_load(connection, dimensions, logger)

        logger.info("ETL COMPLETE | Transaction committed successfully")

    except Exception:
        logger.exception("ETL FAILED | No partial transaction should remain")
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load the dairy-sheep dimensional warehouse from raw_data.xlsx."
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Read, clean, validate, and build dimensions without connecting to PostgreSQL.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        run_etl(validate_only=args.validate_only)
        return 0
    except Exception:
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
