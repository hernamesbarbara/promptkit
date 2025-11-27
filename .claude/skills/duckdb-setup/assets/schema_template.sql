-- DuckDB Schema Template
-- Customize this template for your project's data model

-- =============================================================================
-- CONFIGURATION
-- =============================================================================

-- Adjust based on your system resources
SET memory_limit = '4GB';
SET threads = 4;
SET temp_directory = '/tmp/duckdb';

-- =============================================================================
-- EXTENSIONS
-- =============================================================================

-- Uncomment extensions as needed
INSTALL parquet;
LOAD parquet;

-- INSTALL json;
-- LOAD json;

-- INSTALL httpfs;  -- For S3/HTTP access
-- LOAD httpfs;

-- INSTALL spatial; -- For geospatial data
-- LOAD spatial;

-- =============================================================================
-- SCHEMAS
-- =============================================================================

-- Organize tables into schemas
CREATE SCHEMA IF NOT EXISTS raw;      -- Source data, unmodified
CREATE SCHEMA IF NOT EXISTS staging;  -- Intermediate transformations
CREATE SCHEMA IF NOT EXISTS marts;    -- Final analytical tables

-- =============================================================================
-- RAW TABLES
-- =============================================================================

-- Example: Import from CSV
-- CREATE TABLE raw.source_data AS
-- SELECT * FROM read_csv('path/to/data.csv', header=true, auto_detect=true);

-- Example: Import from Parquet
-- CREATE TABLE raw.source_data AS
-- SELECT * FROM read_parquet('path/to/data.parquet');

-- =============================================================================
-- STAGING TABLES
-- =============================================================================

-- Example: Cleaned and typed data
-- CREATE TABLE staging.cleaned_data AS
-- SELECT
--     CAST(id AS INTEGER) AS id,
--     TRIM(name) AS name,
--     CAST(created_at AS TIMESTAMP) AS created_at
-- FROM raw.source_data
-- WHERE id IS NOT NULL;

-- =============================================================================
-- MART TABLES
-- =============================================================================

-- Example: Analytical aggregation
-- CREATE TABLE marts.daily_summary AS
-- SELECT
--     DATE_TRUNC('day', created_at) AS date,
--     COUNT(*) AS record_count,
--     SUM(amount) AS total_amount
-- FROM staging.cleaned_data
-- GROUP BY 1;

-- =============================================================================
-- VIEWS
-- =============================================================================

-- Example: Latest records view
-- CREATE VIEW marts.latest_records AS
-- SELECT *
-- FROM staging.cleaned_data
-- WHERE created_at >= CURRENT_DATE - INTERVAL '7 days';

-- =============================================================================
-- INDEXES (DuckDB creates these automatically, but you can hint)
-- =============================================================================

-- DuckDB uses adaptive indexing; explicit indexes rarely needed
-- For very large tables, consider partitioning by date:
-- CREATE TABLE marts.partitioned_data AS
-- SELECT * FROM staging.cleaned_data
-- ORDER BY created_at;
