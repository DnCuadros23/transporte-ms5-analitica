import json, os
from datetime import datetime
import boto3
from pymongo import MongoClient

S3 = boto3.client("s3")
BUCKET = os.environ["S3_BUCKET"]

cli = MongoClient(os.environ["MONGO_URI"])
col = cli.get_default_database()["reportes"]

def limpiar(doc):
    doc["_id"] = str(doc["_id"])
    doc["calificacion_id"] = str(doc.get("calificacion_id"))
    for k, v in list(doc.items()):
        if isinstance(v, datetime):
            doc[k] = v.strftime("%Y-%m-%dT%H:%M:%SZ")
    return doc

lineas = []
for doc in col.find({}):
    lineas.append(json.dumps(limpiar(doc), ensure_ascii=False))

S3.put_object(Bucket=BUCKET, Key="raw/reportes/reportes.json",
              Body=("\n".join(lineas)).encode("utf-8"))
print(f"reportes: {len(lineas):,} documentos")
