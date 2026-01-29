# Encoding Issues - Fix Summary

## Problem Overview
The application was encountering UTF-8 encoding errors when loading Portuguese language datasets to PostgreSQL:
```
ERROR: 'utf-8' codec can't decode byte 0xe3 in position 100: invalid continuation byte
```

This error occurs because the CSV files are encoded in **Latin-1 (ISO-8859-1)**, not UTF-8. The byte `0xe3` represents 'ã' in Latin-1, a common character in Portuguese.

---

## Changes Made

### 1. **br_stf_corte_aberta/utils.py** ✓
Fixed two functions that were reading CSV files without proper encoding:

#### Function: `read_csv()` (Line 72)
**Change:** Added `encoding='latin-1'` parameter to `pd.read_csv()`
```python
df = pd.read_csv(
    stf_constants.STF_INPUT.value + arquivo,
    dtype=str,
    encoding='latin-1'  # Added this
)
```

#### Function: `check_for_data()` (Line 172)
**Change:** Added `encoding='latin-1'` parameter to `pd.read_csv()`
```python
df = pd.read_csv(
    stf_constants.STF_INPUT.value + arquivo,
    dtype=str,
    encoding='latin-1'  # Added this
)
```

**Status:** ✓ Already had encoding specified for br_me_cnpj dataset (line 366, 452, 509, 569)

---

### 2. **pipelines/utils/tasks_postgres.py** ✓
Enhanced CSV loading with proper encoding and error handling:

#### Improvements:
1. **Encoding Handling (Line 84)**
   - Changed from default UTF-8 to `encoding='latin-1'`
   - Added fallback to UTF-8 if Latin-1 fails
   - Better error messages for decoding issues

2. **Recursive CSV Search (Line 67-71)**
   - Added recursive glob pattern `**/*.csv` if top-level search fails
   - Handles nested directory structures

3. **Schema Creation (Line 77-84)**
   - Automatically creates PostgreSQL schema if it doesn't exist
   - Prevents "schema not found" errors

4. **Robust File Reading (Line 86-103)**
   - Try-catch for each CSV file individually
   - Continues processing if one file fails
   - Reports rows loaded from each file

5. **Data Type Optimization (Line 109-114)**
   - Converts numeric strings to proper numeric types
   - Improves query performance

6. **Reduced Chunksize (Line 139)**
   - Changed from 10000 to 5000 rows per chunk
   - Better stability with large datasets
   - Reduced memory pressure

7. **Better Error Logging (Line 145-147)**
   - Includes full traceback for debugging
   - Clear error messages with context

---

### 3. **run_br_me_cnpj_postgres.py** ✓
Complete rewrite with robust error handling:

#### Improvements:
1. **Better Logging**
   - Structured output with progress markers
   - Clear section separators
   - Summary report at the end

2. **Table Processing**
   - Processes all 4 tables: Empresas, Socios, Estabelecimentos, Simples
   - Validates CSV files exist before loading
   - Tracks successful and failed tables

3. **Error Handling**
   - Individual error handling for each table
   - Continues processing even if one table fails
   - Exit code indicates overall success/failure (0 = success, 1 = failure)

4. **Validation**
   - Checks for CSV files in output directory
   - Reports number of files found
   - Logs date information from API

5. **Configuration**
   - Uses `schema="public"` for PostgreSQL (standard schema)
   - Tables are created automatically if they don't exist
   - Replaces existing tables (dump_mode="replace")

---

### 4. **br_me_cnpj/utils.py** (Download Retry Logic)
Enhanced exponential backoff strategy:

#### Changes:
- **Max Retries:** 5 → 8 attempts
- **Max Parallel Downloads:** 12 → 8 (reduces server load)
- **Timeout:** 5 min → 10 min per request
- **Backoff Strategy:** 2^attempt → min(2^attempt * 5, 300)
  - Old: 1s, 2s, 4s, 8s, 16s
  - New: 5s, 10s, 20s, 40s, 80s, 160s, 320s (max 5min)
- **Better Error Logging:** Shows attempt count and error details

---

## PostgreSQL Configuration

### Schema Information
- **Default Schema:** `public` (standard PostgreSQL schema)
- **Table Naming:** `{dataset_id}_{table_id}`
  - Example: `br_me_cnpj_empresas`, `br_me_cnpj_socios`, etc.

### Connection Settings
Environment variables used (with defaults):
```python
POSTGRES_HOST = "localhost"
POSTGRES_PORT = "5432"
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "1023a548b"
POSTGRES_DB = "basedosdados"
```

### Table Creation
- Tables are **automatically created** by pandas `.to_sql()`
- Schemas are **automatically created** if they don't exist
- Column types are inferred from data

---

## Testing the Fix

### Run the br_me_cnpj pipeline:
```bash
python run_br_me_cnpj_postgres.py
```

### Expected Output:
```
============================================================
Processando tabela: Empresas
============================================================
Encontrados 10 arquivo(s) CSV
Carregando dados para PostgreSQL: br_me_cnpj.empresas
✓ Tabela empresas carregada com sucesso no PostgreSQL

[... repeat for Socios, Estabelecimentos, Simples ...]

============================================================
RESUMO DA EXECUÇÃO
============================================================
Tabelas processadas com sucesso: 4
  ✓ Empresas
  ✓ Socios
  ✓ Estabelecimentos
  ✓ Simples
```

---

## Key Takeaways

✓ **Encoding:** Brazilian datasets typically use Latin-1, not UTF-8
✓ **Schema:** PostgreSQL `public` schema is the default; no special config needed
✓ **Table Creation:** Handled automatically; no pre-creation required
✓ **Resilience:** Improved download retries and error handling
✓ **Debugging:** Better logging and error messages for troubleshooting

---

## Files Modified
1. ✓ `pipelines/datasets/br_stf_corte_aberta/utils.py`
2. ✓ `pipelines/utils/tasks_postgres.py`
3. ✓ `pipelines/datasets/br_me_cnpj/utils.py`
4. ✓ `run_br_me_cnpj_postgres.py`
