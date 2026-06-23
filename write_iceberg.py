from pyspark.sql import SparkSession
import google.auth
import google.auth.transport.requests

PROJECT_ID = "serve-data-infra-dev"
BUCKET = "gs://iceberg_demo_bucket_zhe"
CATALOG = "iceberg_demo_bucket_zhe"
NAMESPACE = "iceberg_demo_zhe"
TABLE = "orders"

_creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
_creds.refresh(google.auth.transport.requests.Request())

spark = SparkSession.builder \
    .appName("BigLake Iceberg Demo") \
    .config("spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config(f"spark.sql.catalog.{CATALOG}", "org.apache.iceberg.spark.SparkCatalog") \
    .config(f"spark.sql.catalog.{CATALOG}.type", "rest") \
    .config(f"spark.sql.catalog.{CATALOG}.uri", "https://biglake.googleapis.com/iceberg/v1/restcatalog") \
    .config(f"spark.sql.catalog.{CATALOG}.warehouse", f"bl://projects/{PROJECT_ID}/catalogs/{CATALOG}") \
    .config(f"spark.sql.catalog.{CATALOG}.header.x-goog-user-project", PROJECT_ID) \
    .config(f"spark.sql.catalog.{CATALOG}.token", _creds.token) \
    .config(f"spark.sql.catalog.{CATALOG}.io-impl", "org.apache.iceberg.hadoop.HadoopFileIO") \
    .config(f"spark.sql.catalog.{CATALOG}.header.X-Iceberg-Access-Delegation", "vended-credentials") \
    .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
    .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
    .config("spark.hadoop.google.cloud.auth.type", "APPLICATION_DEFAULT") \
    .getOrCreate()

# Create namespace
spark.sql(f"CREATE NAMESPACE IF NOT EXISTS {CATALOG}.{NAMESPACE}")

# Create Iceberg table
spark.sql(f"""
    CREATE TABLE IF NOT EXISTS {CATALOG}.{NAMESPACE}.{TABLE} (
        order_id    INT,
        customer    STRING,
        product     STRING,
        amount      INT,
        order_date  DATE
    )
    USING iceberg
    PARTITIONED BY (order_date)
    TBLPROPERTIES (
        'write.format.default' = 'parquet',
        'write.parquet.compression-codec' = 'snappy'
    )
""")

# Insert sample data
spark.sql(f"""
    INSERT INTO {CATALOG}.{NAMESPACE}.{TABLE} VALUES
    (1, 'Alice', 'Widget A', 100, DATE '2026-06-01'),
    (2, 'Bob',   'Widget B', 200, DATE '2026-06-01'),
    (3, 'Carol', 'Widget C', 150, DATE '2026-06-22'),
    (4, 'Dave',  'Widget A', 300, DATE '2026-06-22')
""")

# Verify
spark.sql(f"SELECT * FROM {CATALOG}.{NAMESPACE}.{TABLE}").show()

print("Done! Iceberg table written to GCS via BigLake Metastore.")
