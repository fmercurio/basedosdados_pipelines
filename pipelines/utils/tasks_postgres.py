"""
Tasks for loading data to PostgreSQL database
"""

import os
import sys
from pathlib import Path

import pandas as pd
from prefect import task
from sqlalchemy import create_engine, text

from pipelines.constants import constants
from pipelines.utils.postgres_config import get_connection_string
from pipelines.utils.utils import log


def get_postgres_connection_string() -> str:
    """
    Get PostgreSQL connection string from environment variables

    Returns:
        str: PostgreSQL connection string in the format postgresql://user:password@host:port/database
    """
    return get_connection_string()


@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=constants.TASK_RETRY_DELAY.value,
)
def load_data_to_postgres(
    data_path: str | Path,
    dataset_id: str,
    table_id: str,
    dump_mode: str = "append",
    schema: str = "public",
) -> bool:
    """
    Load CSV data to PostgreSQL database

    Args:
        data_path: Path to CSV file or directory containing CSV files
        dataset_id: Dataset identifier (used for organization)
        table_id: Table name in PostgreSQL
        dump_mode: How to handle existing data - "append" or "replace"
        schema: PostgreSQL schema name (default: public)

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Ensure UTF-8 encoding for environment and connection
        if sys.platform == "win32":
            # Force UTF-8 for Windows
            os.environ["PYTHONIOENCODING"] = "utf-8"

        # Convert to Path object
        data_path = Path(data_path)

        # Get list of CSV files
        if data_path.is_file():
            csv_files = [data_path]
        else:
            # First try to find CSV files in the directory
            csv_files = list(data_path.glob("*.csv"))

            # If no CSV files found, try recursive search (for partitioned data like estabelecimentos)
            if not csv_files:
                csv_files = list(data_path.glob("**/*.csv"))
                if csv_files:
                    log(
                        f"Found {len(csv_files)} CSV files in subdirectories (partitioned data)"
                    )

            # Se ainda não encontrou, tenta procurar em data=*/sigla_uf=*/ (padrão específico de estabelecimentos)
            if not csv_files:
                csv_files = list(data_path.glob("data=*/sigla_uf=*/*.csv"))
                if csv_files:
                    log(
                        f"Found {len(csv_files)} CSV files using date/state partition pattern"
                    )

        if not csv_files:
            log(f"No CSV files found in {data_path}", level="warning")
            log(
                "Checked paths: *.csv, **/*.csv, and data=*/sigla_uf=*/*.csv",
                level="warning",
            )
            return False

        log(f"Found {len(csv_files)} CSV file(s)")

        # Get connection string
        connection_string = get_postgres_connection_string()
        # Create engine with encoding support
        engine = create_engine(
            connection_string,
            connect_args={"client_encoding": "utf8"},
            pool_pre_ping=True,  # Test connection before using
        )

        # Create schema if it doesn't exist
        try:
            with engine.connect() as connection:
                connection.execute(
                    text(f"CREATE SCHEMA IF NOT EXISTS {schema}")
                )
                connection.commit()
                log(f"Schema '{schema}' created or already exists")
        except Exception as e:
            log(f"Warning: Could not create schema: {e}", level="warning")

        # Load and concatenate all CSV files
        dfs = []
        for csv_file in csv_files:
            log(f"Reading file: {csv_file}")
            try:
                # Try latin-1 first, fallback to utf-8 if it fails
                try:
                    df = pd.read_csv(
                        csv_file,
                        encoding="latin-1",
                        dtype=str,  # Read all as strings to avoid memory issues
                    )
                except UnicodeDecodeError:
                    log(
                        f"Latin-1 decoding failed, trying UTF-8 for {csv_file}"
                    )
                    df = pd.read_csv(
                        csv_file,
                        encoding="utf-8",
                        dtype=str,  # Read all as strings to avoid memory issues
                    )
                dfs.append(df)
                log(f"Successfully loaded {len(df)} rows from {csv_file.name}")
            except Exception as e:
                log(f"Error reading {csv_file}: {e}", level="warning")
                continue

        if not dfs:
            log("No data to load after reading files", level="warning")
            return False

        combined_df = pd.concat(dfs, ignore_index=True)
        log(f"Total: {len(combined_df)} rows from {len(csv_files)} file(s)")

        # Determine if statement
        if_exists = "append" if dump_mode == "append" else "replace"

        # Load to PostgreSQL
        table_name = f"{dataset_id}_{table_id}" if dataset_id else table_id
        log(f"Loading {len(combined_df)} rows to {schema}.{table_name}")

        combined_df.to_sql(
            name=table_name,
            con=engine,
            if_exists=if_exists,
            index=False,
            chunksize=5000,
        )

        log(f"Successfully loaded data to {schema}.{table_name}")
        engine.dispose()
        return True

    except UnicodeDecodeError as e:
        log(
            f"Unicode decode error in database connection. "
            f"Position: {e.start}, Invalid byte: {e.object[e.start : e.start + 1]!r}. "
            f"Check connection string encoding in environment variables.",
            level="error",
        )
        raise
    except Exception as e:
        log(f"Error loading data to PostgreSQL: {e!s}", level="error")
        import traceback

        log(f"Traceback: {traceback.format_exc()}", level="error")
        return False


@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=constants.TASK_RETRY_DELAY.value,
)
def create_table_dev_postgres(
    data_path: str | Path,
    dataset_id: str,
    table_id: str,
    dump_mode: str = "append",
    schema: str = "dev",
) -> bool:
    """
    Create and load data to development PostgreSQL table

    Args:
        data_path: Path to CSV file or directory
        dataset_id: Dataset identifier
        table_id: Table name
        dump_mode: "append" or "replace"
        schema: PostgreSQL schema (default: dev)

    Returns:
        bool: Success status
    """
    return load_data_to_postgres(
        data_path=data_path,
        dataset_id=dataset_id,
        table_id=table_id,
        dump_mode=dump_mode,
        schema=schema,
    )


@task(
    max_retries=constants.TASK_MAX_RETRIES.value,
    retry_delay=constants.TASK_RETRY_DELAY.value,
)
def create_table_prod_postgres(
    data_path: str | Path,
    dataset_id: str,
    table_id: str,
    dump_mode: str = "append",
    schema: str = "public",
) -> bool:
    """
    Create and load data to production PostgreSQL table

    Args:
        data_path: Path to CSV file or directory
        dataset_id: Dataset identifier
        table_id: Table name
        dump_mode: "append" or "replace"
        schema: PostgreSQL schema (default: public)

    Returns:
        bool: Success status
    """
    return load_data_to_postgres(
        data_path=data_path,
        dataset_id=dataset_id,
        table_id=table_id,
        dump_mode=dump_mode,
        schema=schema,
    )


@task
def execute_postgres_query(query: str, schema: str = "public") -> bool:
    """
    Execute an arbitrary SQL query against PostgreSQL

    Args:
        query: SQL query to execute
        schema: Schema context (for logging)

    Returns:
        bool: Success status
    """
    connection_string = get_postgres_connection_string()
    try:
        # Create engine
        engine = create_engine(connection_string)

        with engine.connect() as connection:
            connection.execute(text(query))
            connection.commit()

        log(f"Query executed successfully in {schema}")
        engine.dispose()
        return True

    except Exception as e:
        log(f"Error executing query: {e!s}", level="error")
        return False
