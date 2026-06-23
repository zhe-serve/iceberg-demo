# Iceberg + BigLake Demo

Writes a partitioned Iceberg table to GCS using Spark and the [BigLake Iceberg REST Catalog](https://cloud.google.com/biglake/docs/blms-rest-catalog). The table is registered in BigLake Metastore and queryable from BigQuery.

## Architecture

```
PySpark (Docker)
  └─ Iceberg REST Catalog  ──►  BigLake Metastore API
  └─ HadoopFileIO + GCS Connector  ──►  GCS bucket (Parquet files)
```

## Prerequisites

- Docker Desktop
- `gcloud` CLI authenticated
- A GCP project with billing enabled

## GCP Setup

### 1. Enable APIs

```bash
gcloud services enable biglake.googleapis.com storage.googleapis.com \
  --project=YOUR_PROJECT
```

### 2. Create a GCS bucket

```bash
gcloud storage buckets create gs://YOUR_BUCKET \
  --location=us-central1 \
  --project=YOUR_PROJECT
```

### 3. Create a BigLake Iceberg catalog

```bash
gcloud biglake iceberg catalogs create YOUR_CATALOG \
  --location=us-central1 \
  --project=YOUR_PROJECT
```

The catalog name must match your bucket name (BigLake links them automatically for `CATALOG_TYPE_GCS_BUCKET` catalogs).

### 4. IAM roles

Grant your user account the following roles on the project:

```bash
gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="user:YOU@example.com" \
  --role="roles/biglake.admin"

gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="user:YOU@example.com" \
  --role="roles/serviceusage.serviceUsageConsumer"

gcloud projects add-iam-policy-binding YOUR_PROJECT \
  --member="user:YOU@example.com" \
  --role="roles/storage.objectAdmin"
```

`serviceusage.serviceUsageConsumer` is required because the script bills API calls to your project via the `x-goog-user-project` header.

### 5. Authenticate

```bash
gcloud auth application-default login
```

## Configuration

Edit the variables at the top of `write_iceberg.py`:

```python
PROJECT_ID = "YOUR_PROJECT"
BUCKET     = "gs://YOUR_BUCKET"
CATALOG    = "YOUR_CATALOG"   # must match the BigLake catalog name
NAMESPACE  = "YOUR_NAMESPACE"
TABLE      = "orders"
```

## Running

### macOS / Linux

The gcloud credentials path differs from Windows. Update `docker-compose.yml`:

```yaml
volumes:
  - ~/.config/gcloud:/root/.config/gcloud:ro
```

Then build and run:

```bash
docker-compose build
docker-compose run --rm spark python3 /app/write_iceberg.py
```

### Windows (Git Bash / PowerShell)

The `docker-compose.yml` already uses `${APPDATA}/gcloud` which points to
`%APPDATA%\gcloud` — the default location for `gcloud auth application-default login` on Windows.

```bash
docker-compose build
MSYS_NO_PATHCONV=1 docker-compose run --rm spark python3 /app/write_iceberg.py
```

> **Note:** `MSYS_NO_PATHCONV=1` prevents Git Bash from mangling the `/app/` path.

## Expected output

```
+--------+--------+--------+------+----------+
|order_id|customer| product|amount|order_date|
+--------+--------+--------+------+----------+
|       1|   Alice|Widget A|   100|2026-06-01|
|       2|     Bob|Widget B|   200|2026-06-01|
|       3|   Carol|Widget C|   150|2026-06-22|
|       4|    Dave|Widget A|   300|2026-06-22|
+--------+--------+--------+------+----------+

Done! Iceberg table written to GCS via BigLake Metastore.
```

## Querying from BigQuery

Once the table is written, you can query it directly in BigQuery:

```sql
SELECT * FROM `YOUR_PROJECT`.YOUR_NAMESPACE.orders;
```

## JAR versions

| JAR | Version | Purpose |
|-----|---------|---------|
| `iceberg-spark-runtime-3.5_2.12` | 1.9.1 | Iceberg + Spark integration |
| `gcs-connector-hadoop3` | latest | GCS filesystem for Hadoop |
