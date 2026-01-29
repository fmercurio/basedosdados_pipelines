"""
PostgreSQL configuration utilities
"""

import os
from urllib.parse import quote


def get_db_config() -> dict:
    """
    Get PostgreSQL database configuration from environment variables

    Returns:
        dict: Database configuration with host, port, user, password, and name
    """
    return {
        "host": os.getenv("POSTGRES_HOST", "localhost"),
        "port": os.getenv("POSTGRES_PORT", "5432"),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", "1023a548b"),
        "name": os.getenv("POSTGRES_DB", "postgres"),
    }


def get_connection_string(db_config: dict = None) -> str:
    """
    Build PostgreSQL connection string from config

    Args:
        db_config: Database configuration dictionary. If None, uses get_db_config()

    Returns:
        str: PostgreSQL connection string
    """
    if db_config is None:
        db_config = get_db_config()

    encoded_password = quote(db_config["password"], safe="")
    return f"postgresql://{db_config['user']}:{encoded_password}@{db_config['host']}:{db_config['port']}/{db_config['name']}?client_encoding=utf8"
