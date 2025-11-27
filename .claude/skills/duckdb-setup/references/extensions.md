# DuckDB Extensions Reference

## Core Extensions

### parquet
**Purpose:** Read and write Parquet files (columnar format)
```sql
INSTALL parquet;
LOAD parquet;

-- Read single file
SELECT * FROM read_parquet('file.parquet');

-- Read multiple files with glob
SELECT * FROM read_parquet('data/*.parquet');

-- Write to parquet
COPY table_name TO 'output.parquet' (FORMAT PARQUET);
```

### json
**Purpose:** Read and write JSON/JSONL files
```sql
INSTALL json;
LOAD json;

-- Read JSON
SELECT * FROM read_json('file.json');

-- Read newline-delimited JSON
SELECT * FROM read_json('file.jsonl', format='newline_delimited');

-- Auto-detect structure
SELECT * FROM read_json_auto('file.json');
```

### httpfs
**Purpose:** Read files from HTTP, S3, GCS, Azure Blob
```sql
INSTALL httpfs;
LOAD httpfs;

-- HTTP
SELECT * FROM read_parquet('https://example.com/data.parquet');

-- S3
SET s3_region = 'us-east-1';
SET s3_access_key_id = 'key';
SET s3_secret_access_key = 'secret';
SELECT * FROM read_parquet('s3://bucket/path/file.parquet');

-- GCS
SET s3_endpoint = 'storage.googleapis.com';
SELECT * FROM read_parquet('s3://bucket/path/file.parquet');
```

### spatial
**Purpose:** Geospatial data types and functions
```sql
INSTALL spatial;
LOAD spatial;

-- Create geometry
SELECT ST_Point(longitude, latitude) AS geom FROM locations;

-- Spatial operations
SELECT ST_Distance(geom1, geom2) FROM spatial_data;
SELECT ST_Contains(polygon, point) FROM areas, points;

-- Read shapefiles
SELECT * FROM ST_Read('file.shp');
```

## Data Source Extensions

### sqlite
**Purpose:** Query SQLite databases directly
```sql
INSTALL sqlite;
LOAD sqlite;

-- Attach SQLite database
ATTACH 'database.sqlite' AS sqlite_db (TYPE sqlite);
SELECT * FROM sqlite_db.table_name;
```

### postgres
**Purpose:** Query PostgreSQL databases
```sql
INSTALL postgres;
LOAD postgres;

-- Attach PostgreSQL
ATTACH 'postgresql://user:pass@host:5432/db' AS pg (TYPE postgres);
SELECT * FROM pg.schema.table_name;

-- Or use postgres_scan
SELECT * FROM postgres_scan('postgresql://...', 'schema', 'table');
```

### mysql
**Purpose:** Query MySQL databases
```sql
INSTALL mysql;
LOAD mysql;

ATTACH 'mysql://user:pass@host:3306/db' AS mysql_db (TYPE mysql);
SELECT * FROM mysql_db.table_name;
```

### excel
**Purpose:** Read Excel files (.xlsx, .xls)
```sql
INSTALL excel;
LOAD excel;

-- Read specific sheet
SELECT * FROM read_xlsx('file.xlsx', sheet='Sheet1');

-- Read all sheets
SELECT * FROM read_xlsx('file.xlsx');
```

## Utility Extensions

### fts
**Purpose:** Full-text search
```sql
INSTALL fts;
LOAD fts;

-- Create FTS index
PRAGMA create_fts_index('table_name', 'id', 'text_column');

-- Search
SELECT * FROM table_name
WHERE text_column MATCH 'search terms';
```

### icu
**Purpose:** International Components for Unicode (collation, case folding)
```sql
INSTALL icu;
LOAD icu;

-- Case-insensitive collation
SELECT * FROM table_name
ORDER BY name COLLATE NOCASE;
```

### tpch
**Purpose:** TPC-H benchmark data generation
```sql
INSTALL tpch;
LOAD tpch;

-- Generate TPC-H data (scale factor 1 = ~1GB)
CALL dbgen(sf=1);
```

### tpcds
**Purpose:** TPC-DS benchmark data generation
```sql
INSTALL tpcds;
LOAD tpcds;

CALL dsdgen(sf=1);
```

## Extension Management

```sql
-- List available extensions
SELECT * FROM duckdb_extensions();

-- List installed extensions
SELECT * FROM duckdb_extensions() WHERE installed;

-- List loaded extensions
SELECT * FROM duckdb_extensions() WHERE loaded;

-- Force update an extension
FORCE INSTALL extension_name;

-- Set custom extension directory
SET extension_directory = '/path/to/extensions';
```

## Version Compatibility

Extensions are versioned with DuckDB. When upgrading DuckDB:
1. Extensions may need reinstallation
2. Check release notes for breaking changes
3. Use `FORCE INSTALL` to update

## Custom Extension Repository

```sql
-- Use custom repository
SET custom_extension_repository = 'https://example.com/extensions';
INSTALL my_extension FROM custom_extension_repository;
```
