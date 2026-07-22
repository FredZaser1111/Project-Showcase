# MariaDB portability notes

Primary demo DBMS is **PostgreSQL 16** (`docker compose` on port 5433).

To run the same model on MariaDB / MySQL:

| PostgreSQL | MariaDB equivalent |
| --- | --- |
| `UUID` | `CHAR(36)` (store UUID strings) |
| `TIMESTAMPTZ` | `DATETIME(6)` |
| `JSONB` | `JSON` |
| `NUMERIC(12,2)` | `DECIMAL(12,2)` |
| `CREATE SEQUENCE` / `nextval` | `AUTO_INCREMENT` on a helper table, or `UUID()` |
| `CREATE OR REPLACE VIEW` | Supported as-is in MariaDB 10.6+ |
| `FOR UPDATE` row locks | Supported InnoDB |

Application code uses ANSI SQL via JDBC (`NamedParameterJdbcTemplate`). Avoid Postgres-only operators in Java repositories beyond `CAST(... AS jsonb)` — for MariaDB swap to plain JSON string insert.

See [`schema/parts_inventory.sql`](schema/parts_inventory.sql) header comments for the same mapping.
