import csv, io, os
import boto3, psycopg2

S3 = boto3.client("s3")
BUCKET = os.environ["S3_BUCKET"]
DSN = os.environ["PG_DSN"]

TABLAS = {
    "usuarios":    ["id","nombre","apellido","email","telefono","distrito",
                    "fecha_nacimiento","fecha_registro","activo"],
    "conductores": ["id","nombre","apellido","email","telefono","nro_licencia",
                    "distrito_base","fecha_ingreso","calificacion_promedio","activo"],
    "vehiculos":   ["id","conductor_id","placa","marca","modelo","anio",
                    "color","capacidad","tipo_servicio"],
}

cn = psycopg2.connect(DSN)
for tabla, columnas in TABLAS.items():
    cur = cn.cursor()
    cur.execute(f"SELECT {', '.join(columnas)} FROM {tabla} ORDER BY id")
    buf = io.StringIO()
    w = csv.writer(buf, quoting=csv.QUOTE_MINIMAL, lineterminator="\n")
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
