# MS5 — Analítica (S3 + Glue + Athena)


## Contenido
- `ingesta01/` — pull de PostgreSQL → CSV → S3
- `ingesta03/` — pull de MongoDB → JSON Lines → S3
- `ms5/` — API analítica FastAPI + boto3 sobre Athena
- `ddl_postgres.sql` — DDL provisional de MS1
- `docker-compose.dev.yml` — Postgres 16 y Mongo 7 locales

## Imágenes públicas
- `denilsoncv23/transporte-ingesta01:1.0`
- `denilsoncv23/transporte-ingesta03:1.0`
- `denilsoncv23/transporte-ms5:1.0`

## Datalake
Bucket `transporte-datalake-dncuadros`, base Glue `transporte_urbano`.
