# PostgreSQL Connection Encoding Fix

## Problem
The error occurred when psycopg2 (PostgreSQL driver) tried to decode the connection parameters as UTF-8, but the system had non-UTF-8 encoded data:

```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe3 in position 100: invalid continuation byte
```

This happened during the `engine.connect()` call, before any data transfer.

## Root Cause
- The environment variables or connection string contained data that couldn't be decoded as UTF-8
- SQLAlchemy/psycopg2 wasn't explicitly configured for proper character encoding
- No URL encoding for special characters in the password

## Solution Implemented

### 1. URL Encode Password
Added URL encoding for the database password to safely handle special characters:
```python
from urllib.parse import quote
encoded_password = quote(db_password, safe='')
```

### 2. Add Encoding to Connection String
Added `client_encoding=utf8` parameter to the PostgreSQL connection string:
```python
connection_string = f"postgresql://{db_user}:{encoded_password}@{db_host}:{db_port}/{db_name}?client_encoding=utf8"
```

### 3. Configure SQLAlchemy Engine
Added encoding configuration to the SQLAlchemy engine creation:
```python
engine = create_engine(
    connection_string,
    connect_args={'client_encoding': 'utf8'},
    pool_pre_ping=True,  # Test connection before using
)
```

## File Modified
- `pipelines/utils/tasks_postgres.py`

## Changes Summary
1. ✓ Added `from urllib.parse import quote` import
2. ✓ URL-encode the database password
3. ✓ Add `client_encoding=utf8` to connection string
4. ✓ Add `connect_args` and `pool_pre_ping` to SQLAlchemy engine
5. ✓ Removed inline import (moved to top of file)

## Testing
Run the pipeline again:
```bash
python run_br_me_cnpj_postgres.py
```

The connection should now properly handle character encoding at all levels:
- Connection string level (client_encoding parameter)
- SQLAlchemy engine level (connect_args)
- Data transfer level (already fixed with latin-1 encoding for CSVs)
