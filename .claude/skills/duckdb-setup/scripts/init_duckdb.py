#!/usr/bin/env python3
"""
DuckDB Database Initialization Script

Usage:
    python init_duckdb.py <database_path> [--memory-limit <size>] [--threads <n>]
    python init_duckdb.py analytics.duckdb --memory-limit 4GB --threads 4

Creates a new DuckDB database with common extensions and configuration.
"""

import argparse
import sys
from pathlib import Path

try:
    import duckdb
except ImportError:
    print("Error: duckdb not installed. Run: pip install duckdb")
    sys.exit(1)


COMMON_EXTENSIONS = [
    "parquet",
    "json",
    "httpfs",
]

DEFAULT_CONFIG = {
    "enable_progress_bar": "true",
    "enable_object_cache": "true",
}


def init_database(
    db_path: str,
    memory_limit: str | None = None,
    threads: int | None = None,
    extensions: list[str] | None = None,
) -> duckdb.DuckDBPyConnection:
    """Initialize a DuckDB database with configuration and extensions."""

    config = DEFAULT_CONFIG.copy()
    if memory_limit:
        config["memory_limit"] = memory_limit
    if threads:
        config["threads"] = str(threads)

    con = duckdb.connect(db_path, config=config)

    # Install and load extensions
    ext_list = extensions or COMMON_EXTENSIONS
    for ext in ext_list:
        try:
            con.execute(f"INSTALL {ext}")
            con.execute(f"LOAD {ext}")
            print(f"Loaded extension: {ext}")
        except Exception as e:
            print(f"Warning: Could not load {ext}: {e}")

    return con


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a DuckDB database with common configuration"
    )
    parser.add_argument(
        "database",
        help="Path to database file (use :memory: for in-memory)"
    )
    parser.add_argument(
        "--memory-limit",
        help="Memory limit (e.g., 4GB, 512MB)"
    )
    parser.add_argument(
        "--threads",
        type=int,
        help="Number of threads for parallel execution"
    )
    parser.add_argument(
        "--extensions",
        nargs="+",
        help="Extensions to install (default: parquet, json, httpfs)"
    )

    args = parser.parse_args()

    db_path = args.database
    if db_path != ":memory:":
        path = Path(db_path)
        if path.exists():
            print(f"Database already exists: {db_path}")
            response = input("Overwrite? [y/N]: ")
            if response.lower() != "y":
                print("Aborted.")
                sys.exit(0)

    con = init_database(
        db_path,
        memory_limit=args.memory_limit,
        threads=args.threads,
        extensions=args.extensions,
    )

    # Print summary
    print(f"\nDatabase initialized: {db_path}")
    print("\nConfiguration:")
    for row in con.execute("SELECT name, value FROM duckdb_settings() WHERE name IN ('memory_limit', 'threads', 'temp_directory')").fetchall():
        print(f"  {row[0]}: {row[1]}")

    print("\nLoaded extensions:")
    for row in con.execute("SELECT extension_name FROM duckdb_extensions() WHERE loaded = true").fetchall():
        print(f"  {row[0]}")

    con.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
