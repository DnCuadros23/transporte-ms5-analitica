import csv, io, os
import boto3, mysql.connector

S3 = boto3.client("s3")
BUCKET = os.environ["S3_BUCKET"]

TABLAS = ["viajes", "paradas", "tarifas"]

cn = mysql.connector.connect(
    host=os.environ.get("MYSQL_HOST", "localhost"),
    user=os.environ.get("MYSQL_USER", "app_ms2"),
    password=os.environ.get("MYSQL_PASS", "local"),
    database=os.environ.get("MYSQL_DB", "viajes_db"),
)

for tabla in TABLAS:
    cur = cn.cursor()
    cur.execute(f"SELECT * FROM {tabla} ORDER BY id")   # 100% de los registros
    columnas = [d[0] for d in cur.description]
    buf = io.StringIO()
    w = csv.writer(buf, quoting=csv.QUOTE_MINIMAL)
    w.writerow(columnas)
    n = 0
    for fila in cur:
        w.writerow(["" if v is None else v for v in fila])
        n += 1
    S3.put_object(Bucket=BUCKET, Key=f"raw/{tabla}/{tabla}.csv",
                  Body=buf.getvalue().encode("utf-8"))
    print(f"{tabla}: {n:,} filas -> s3://{BUCKET}/raw/{tabla}/{tabla}.csv")
    cur.close()
cn.close()
