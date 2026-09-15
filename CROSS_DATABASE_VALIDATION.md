# Cross-database validation

The automated workflow executes the same generated 10,000-order ELT smoke test against SQLite, PostgreSQL 16, and MySQL 8.4. It creates dimensional and fact tables, bulk-loads non-sensitive synthetic records, and verifies total rows, unique order keys, and completed-order counts.

SQL Server, Snowflake, Teradata, and Oracle remain awareness-level technologies and are not represented as hands-on implementations.

Run locally with SQLite:

```bash
pip install -r requirements-cross-db.txt
python db_smoke_test.py
```

The GitHub Actions page provides independently visible run results for PostgreSQL and MySQL.
