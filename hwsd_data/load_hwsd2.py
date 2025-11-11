#!/usr/bin/env python
"""
Load HWSD2 CSV files into DuckDB database.

This script creates a DuckDB database from the HWSD2 CSV files using the
schema defined in hwsd2_duckdb_schema.sql.

Usage:
    uv run python load_hwsd2.py [output_db_path]

Default output: hwsd2.db
"""

import sys
from pathlib import Path
import duckdb


def load_hwsd2(db_path: str = "hwsd2.db", csv_dir: str = "HWSD2_csv") -> None:
    """
    Load HWSD2 CSV files into a DuckDB database.

    Args:
        db_path: Path to output DuckDB database file
        csv_dir: Path to directory containing CSV files

    Examples:
        >>> # This will create hwsd2.db in current directory
        >>> load_hwsd2()
        >>> # Use custom paths
        >>> load_hwsd2("my_hwsd.db", "data/HWSD2_csv")
    """
    csv_path = Path(csv_dir)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV directory not found: {csv_path}")

    print(f"Creating DuckDB database: {db_path}")
    print(f"Loading from CSV directory: {csv_path}")

    # Connect to database (creates if doesn't exist)
    conn = duckdb.connect(db_path)

    # Load schema from SQL file
    schema_file = Path(__file__).parent / "hwsd2_duckdb_schema.sql"
    if not schema_file.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    print("\nReading schema...")
    with open(schema_file) as f:
        schema_sql = f.read()

    # Split SQL into statements and execute
    # We need to modify the COPY statements to use absolute paths
    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

    print("\nCreating tables...")
    table_count = 0
    copy_count = 0

    for stmt in statements:
        if not stmt:
            continue

        # Modify COPY statements to use the correct path
        if stmt.strip().startswith('COPY'):
            # Extract the CSV filename
            parts = stmt.split("'")
            if len(parts) >= 2:
                csv_file = parts[1]
                # Replace with absolute path
                full_path = csv_path / csv_file.replace('HWSD2_csv/', '')
                stmt = stmt.replace(f"'{csv_file}'", f"'{full_path}'")
                print(f"  Loading: {full_path.name}")
                copy_count += 1
        elif stmt.strip().startswith('CREATE TABLE'):
            table_name = stmt.split()[2]
            print(f"  Creating: {table_name}")
            table_count += 1
        elif stmt.strip().startswith('CREATE INDEX'):
            continue  # Skip printing indexes

        try:
            conn.execute(stmt)
        except Exception as e:
            print(f"Warning: Failed to execute statement: {e}")
            print(f"Statement: {stmt[:100]}...")

    print(f"\nComplete!")
    print(f"  Tables created: {table_count}")
    print(f"  Files loaded: {copy_count}")

    # Print some basic statistics
    print("\nDatabase statistics:")
    print(f"  HWSD2_LAYERS rows: {conn.execute('SELECT COUNT(*) FROM HWSD2_LAYERS').fetchone()[0]:,}")
    print(f"  HWSD2_SMU rows: {conn.execute('SELECT COUNT(*) FROM HWSD2_SMU').fetchone()[0]:,}")
    domain_count = conn.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name LIKE 'D_%'").fetchone()[0]
    print(f"  Domain tables: {domain_count}")

    # Show a sample query
    print("\nSample data from HWSD2_LAYERS:")
    result = conn.execute("""
        SELECT
            HWSD2_SMU_ID,
            LAYER,
            TOPDEP,
            BOTDEP,
            SAND,
            SILT,
            CLAY,
            ORG_CARBON,
            PH_WATER
        FROM HWSD2_LAYERS
        LIMIT 5
    """).fetchdf()
    print(result.to_string())

    conn.close()
    print(f"\nDatabase saved to: {db_path}")


def main():
    """Main entry point for command-line usage."""
    db_path = sys.argv[1] if len(sys.argv) > 1 else "hwsd2.db"

    # Determine CSV directory relative to this script
    script_dir = Path(__file__).parent
    csv_dir = script_dir / "HWSD2_csv"

    try:
        load_hwsd2(str(db_path), str(csv_dir))
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
